#include "experiments.h"
#include "noveltyset.h"

#include "datarec.h"
#include "maze.h"
#include "graph.h"

#include "histogram.h"
#include "calc_evol.h"
#include "genome.h"
//#define DEBUG_OUTPUT 1

#include <algorithm>
#include <vector>
#include <cstring>
#include <iostream>
#include <fstream>
#include <math.h>

#include "population.h"
#include "population_state.h"

#define MAX_NICHES 300000
#define GENOME_SIZE_LIMIT 300

//The current environment
static bool debugflag=false;
static Environment* env;
static vector<Environment*> envList;
static ofstream *logfile=NULL;

void set_debug_flag(bool val) {
 debugflag=val;
}

//for real-time plotting
static vector<float> best_fits;
plot front_plot;
plot fitness_plot;
plot behavior_plot;


using namespace std;

enum novelty_measure_type { novelty_fitness, novelty_sample, novelty_accum, novelty_sample_free, novelty_outcome };
static novelty_measure_type novelty_measure = novelty_sample;

enum fitness_measure_type { fitness_uniform,fitness_goal, fitness_drift, fitness_std,fitness_rnd,fitness_spin,fitness_changegoal,fitness_collisions,fitness_reachone ,fitness_aoi,fitness_collgoal};

static fitness_measure_type fitness_measure = fitness_goal;

static int maxgens;
static bool mc_no_collision=false;
static bool mc_reach_onepoint=false;
bool age_objective=false;
bool population_dirty=false;
static bool extinction=true;

bool set_no_collision(bool no) {
    mc_no_collision=no;
}
bool set_reach_onepoint(bool ro) {
    mc_reach_onepoint=ro;
}
bool get_age_objective() {
    return age_objective;
}
void set_age_objective(bool ao) {
    age_objective=ao;
}

static int number_of_samples = 1;
static int simulated_timesteps = 400;
bool seed_mode = false;
char seed_name[100]="";
bool minimal_criteria=false;
bool evaluate_switch=false;
static bool goal_attract=true;
static bool constraint_switch=false;
static bool area_of_interest=false;
static bool rand_repl=false;
char output_dir[200]="";
static int param=-1;
static int push_back_size = 20;


void set_extinction(bool _ext) {
    extinction=_ext;
}
static Point extinction_point(0.0,0.0);
static float extinction_radius=50.0;
static int change_extinction_length=5;

void change_extinction_point() {
    float minx,maxx,miny,maxy;
    envList[0]->get_range(minx,miny,maxx,maxy);

    extinction_point.x = randfloat()*(maxx-minx)+minx;
    extinction_point.y = randfloat()*(maxy-miny)+miny;
    if (extinction)
        population_dirty=true;
}

bool extinct(Point k) {
    if (k.distance(extinction_point)<extinction_radius)
        return true;
    return false;
}


void set_evaluate(bool val) {
    evaluate_switch=val;
}
void set_random_replace(bool val)
{
    rand_repl = val;
}

void set_aoi(bool val)
{
    area_of_interest=val;
}

void  set_constraint_switch(bool val)
{
    constraint_switch=val;
}
void set_minimal_criteria(bool mc)
{
    minimal_criteria=mc;
}

void set_goal_attract(bool ga)
{
    goal_attract=ga;
}

void set_samples(int s)
{
    number_of_samples=s;
}

void set_timesteps(int s)
{
    simulated_timesteps=s;
}

void set_seed(string s)
{
    strcpy(seed_name,s.c_str());
    if (strlen(seed_name)>0)
        seed_mode=true;
}

void set_fit_measure(string m)
{
    if (m=="uniform")
        fitness_measure=fitness_uniform;
    if (m=="reachone")
        fitness_measure=fitness_reachone;
    if (m=="rnd")
        fitness_measure=fitness_rnd;
    if (m=="std")
        fitness_measure=fitness_std;
    if (m=="drift")
        fitness_measure=fitness_drift;
    if (m=="goal")
        fitness_measure=fitness_goal;
    if (m=="spin")
        fitness_measure=fitness_spin;
    if (m=="changegoal")
        fitness_measure=fitness_changegoal;
    if (m=="collisions")
        fitness_measure=fitness_collisions;
    if (m=="aoi")
        fitness_measure=fitness_aoi;
    if (m=="nocollide_goal")
        fitness_measure=fitness_collgoal;
    cout << "Fitness measure " << fitness_measure << endl;
}

void set_nov_measure(string m)
{
    if (m=="fitness")
        novelty_measure=novelty_fitness;
    if (m=="std" || m=="sample")
        novelty_measure=novelty_sample;
    if (m=="accum")
        novelty_measure=novelty_accum;
    if (m=="sample_free")
        novelty_measure=novelty_sample_free;
    if (m=="outcome")
        novelty_measure=novelty_outcome;
    cout << "Novelty measure " << novelty_measure << endl;
}


//novelty metric for maze simulation
//measures how different two behaviors are
float maze_novelty_metric(noveltyitem* x,noveltyitem* y)
{
    float diff = 0.0;
    for (int k=0; k<(int)x->data.size(); k++)
    {
        diff+=hist_diff(x->data[k],y->data[k]);
    }
    return diff;
}

static void read_in_environments(const char* mazefile, vector<Environment*>& envLst)
{
    ifstream listfile(mazefile);

    while (!listfile.eof())
    {
        string filename;
        getline(listfile,filename);
        if (filename.length() == 0)
            break;
        cout << "Reading maze: " << filename << endl;
        Environment* new_env = new Environment(filename.c_str());
        envLst.push_back(new_env);
    }

}

//simulation for limited capacity niche model from paper
class passive_niche {
public:

    //a niche is a collection of organisms
    vector<Organism*> niches[MAX_NICHES];

    //has a particular niche been explored yet?
    bool explored[MAX_NICHES];

    //what order have the niches been explored?
    int order[MAX_NICHES];


    int niche_size; //how many individuals can fit in a niche
    int evals;  //how many evaluations should be run?
    int density; //how dense should the grid of niches be created over possible behaviors
    int nc; //number of niches discovered

    bool firstsolved; //keep track if a 'solution' to the maze has been evolved
    bool random; //should niches be completely random? or are they based on where the maze navigator ends?

    float minx,miny,maxx,maxy;

    //initializer
    passive_niche(bool _r=false) {
        random=_r;
        density=30;
        niche_size=10;
        evals=250001;
        for(int i=0; i<MAX_NICHES; i++) explored[i]=false;
        for(int i=0; i<MAX_NICHES; i++) order[i]=false;
        nc=0;
        firstsolved=true;
    }

    //calculate evolvability over all niches
    void calc_evolvability(char*fn) {
        for(int i=0; i<nc; i++) {
            cout << "evolvability niche " << i << endl;
            //estimate niche's evolvability by taking 5 individuals at random from the niche
            for(int j=0; j<5; j++) {
                int ns=niches[order[i]].size();
                Organism *org = niches[order[i]][randint(0,ns-1)];
                evolvability(org,fn);
            }
        }
    }


    void print_niches() {
        for(int x=0; x<density; x++)
        {
            for(int y=0; y<density; y++)
            {
                cout << explored[x*density+y];
            }
            cout <<endl;
        }
    }

    int scale(int d,float val, float min,float max) {
        return (int)(d*(val-min)/((max+0.01f)-min));
    }

    //function that maps an organism into its niche
    int map_into_niche(Organism* o) {
        float x= o->noveltypoint->data[0][0];
        float y= o->noveltypoint->data[0][1];
        if (!random)
            return ((int)x)/10*300+((int)y)/10; //to match other simulations
        else
            return rand()%400;
        //return scale(density,x,minx,maxx)*density+scale(density,y,miny,maxy);
    }

    //insert an entire population into niches
    void insert_population(Population* pop) {
        vector<Organism*>::iterator curorg;
        for (curorg = (pop->organisms).begin(); curorg != pop->organisms.end(); ++curorg) {
            insert_org((*curorg));
        }
    }

    //insert an organism into a niche
    void insert_org(Organism* org) {
        int target_niche = map_into_niche(org);
        if(target_niche<0)
            return;
        int sz=niches[target_niche].size();
        if(sz==0) {
            explored[target_niche]=true;
            order[nc]=target_niche;
            nc++;
        }
        if(sz>=niche_size) {
            //return;
            remove_one_from_niche(target_niche);
        }
        niches[target_niche].push_back(org);
    }

    void remove_one_from_niche(int n) {
        int to_rem = randint(0,niches[n].size()-1);
        Organism* o = niches[n][to_rem];
        niches[n].erase(niches[n].begin()+to_rem);
        delete o;
    }

    int exploredcount() {
        int c=0;
        for(int i=0; i<MAX_NICHES; i++) if (explored[i]) c++;
        return  c;
    }

    void run_niche(Population* initpop) {

        envList[0]->get_range(minx,miny,maxx,maxy);
        insert_population(initpop);

        int e=0;
        int num_niches=density*density;

        while(e<evals) {
            cout << "evals " << e <<endl;
            cout << "explored " << exploredcount() << endl;
            vector<Organism*> children;

            int conn=0;
            int nodes=0;
            int count=0;

            for(int i=0; i<num_niches; i++) {
                if(niches[i].size()==0)
                    continue;
                Genome *new_gene= new Genome(*niches[i][randint(0,niches[i].size()-1)]->gnome);
                mutate_genome(new_gene,true);
                Organism* new_org= new Organism(0.0,new_gene,0);
                initpop->evaluate_organism(new_org);
                if(new_org->datarec->ToRec[3] > 0 && firstsolved) {
                    cout << "solved " << e << endl;
                    firstsolved=false;
                }
                nodes+=new_org->net->nodecount();
                conn+=new_org->net->linkcount();
                count++;
                children.push_back(new_org);
                e++;
                int upcnt=10000;
                if(e%upcnt==0) {
                    char fn[100];
                    sprintf(fn,"%s_evolvability%d.dat",output_dir,e/upcnt);
                    calc_evolvability(fn);
                }
            }
            cout << "avgnodes" << ((float)nodes)/count << endl;
            cout << "avgconns" << ((float)conn)/count << endl;

            for(vector<Organism*>::iterator it=children.begin(); it!=children.end(); it++)
                insert_org(*it);

        }
    }

};

void enumerate_behaviors(const char* mazefile, long long par,const char* outfile,int count) {
    read_in_environments(mazefile,envList);

    ofstream ofile(outfile);
    ofile << par << endl;

    for(int x=0; x<count; x++) {
        Genome *g = new Genome(3,2,2,2);

        long long partemp=par;
        for(int i=17; i>=0; i--) {
            long long val = (partemp % 3) - 1;
            g->genes[i]->lnk->weight = (double)val;
            partemp /= 3;
        }

        Organism* new_org= new Organism(0.0,g,0);
        noveltyitem* nov_item = maze_novelty_map(new_org);
        ofile << nov_item->data[0][0] << " " << nov_item->data[0][1] << endl;
        delete nov_item;
        delete new_org;
        par++;
    }
}

//passive algorithm
Population *maze_passive(char* outputdir,const char* mazefile,int par,const char* genes,bool novelty) {

    Population *pop;
    Genome *start_genome;
    char curword[20];

    int id;

    read_in_environments(mazefile,envList);

    push_back_size=par;
    if (outputdir!=NULL) strcpy(output_dir,outputdir);

    if (!seed_mode)
        strcpy(seed_name,genes);

    ifstream iFile(seed_name,ios::in);

    cout<<"START MAZE NAVIGATOR NICHED MODEL"<<endl;
    if (!seed_mode)
    {
        cout<<"Reading in the start genome"<<endl;
    }
    else
        cout<<"Reading in the seed genome" <<endl;

    //Read in the start Genome
    iFile>>curword;
    iFile>>id;
    cout<<"Reading in Genome id "<<id<<endl;
    start_genome=new Genome(id,iFile);
    iFile.close();

    cout<<"Start Genome: "<<start_genome<<endl;

    //Spawn the Population from starter gene
    cout<<"Spawning Population off Genome"<<endl;
    if (!seed_mode)
        pop=new Population(start_genome,NEAT::pop_size);
    else
    {
        pop=new Population(seed_name);//start_genome,NEAT::pop_size,0.0);
        if (evaluate_switch) {
            int dist=0;
            double evol=0.0;
            evolvability(pop->organisms[0],"dummyfile",&dist,&evol,true);
            cout << endl << dist << " " << evol << endl;
            return 0;
        }

    }
    cout<<"Verifying Spawned Pop"<<endl;
    pop->verify();
    pop->set_evaluator(&maze_novelty_map);
    pop->evaluate_all();

    passive_niche pn(novelty);
    pn.run_niche(pop);

    //clean up
    delete env;
    return pop;
}

//novelty maze navigation run
Population *maze_novelty_realtime(char* outputdir,const char* mazefile,int par,const char* genes,bool novelty) {

    Population *pop;
    Genome *start_genome;
    char curword[20];

    int id;


    //crgate new maze environment
    //env=new Environment(mazefile);
    //read in environments
    read_in_environments(mazefile,envList);

    //param=par;
    push_back_size=par;
    if (outputdir!=NULL) strcpy(output_dir,outputdir);

    if (!seed_mode)
        strcpy(seed_name,genes);
    //starter genes file
    ifstream iFile(seed_name,ios::in);

    cout<<"START MAZE NAVIGATOR NOVELTY REAL-TIME EVOLUTION VALIDATION"<<endl;
    if (!seed_mode)
    {
        cout<<"Reading in the start genome"<<endl;
    }
    else
        cout<<"Reading in the seed genome" <<endl;

    //Read in the start Genome
    iFile>>curword;
    iFile>>id;
    cout<<"Reading in Genome id "<<id<<endl;
    start_genome=new Genome(id,iFile);
    iFile.close();

    cout<<"Start Genome: "<<start_genome<<endl;

    //Spawn the Population from starter gene
    cout<<"Spawning Population off Genome"<<endl;
    if (!seed_mode)
        pop=new Population(start_genome,NEAT::pop_size);
    else
    {
        pop=new Population(seed_name);//start_genome,NEAT::pop_size,0.0);
        if (evaluate_switch) {
	    set_debug_flag(true);
            int dist=0;
            double evol=0.0;
            //evolvability(pop->organisms[0],"dummyfile",&dist,&evol,true);
            pop->set_evaluator(&maze_novelty_map);
            pop->evaluate_all();
                  
            //cout << endl << dist << " " << evol << endl;
            cout << pop->organisms[0]->fitness << endl;
            return 0;
        }

    }
    cout<<"Verifying Spawned Pop"<<endl;
    pop->verify();
    pop->set_evaluator(&maze_novelty_map);
    //pop->set_compatibility(&behavioral_compatibility);
    //Start the evolution loop using rtNEAT method calls
    maze_novelty_realtime_loop(pop,novelty);

    //clean up
    delete env;
    return pop;
}

//actual rtNEAT loop for novelty maze navigation runs
int maze_novelty_realtime_loop(Population *pop,bool novelty) {
    bool firstflag=false; //indicates whether the maze has been solved yet
    bool weakfirst=false;
    vector<Organism*>::iterator curorg;
    vector<Species*>::iterator curspecies;
    vector<Species*>::iterator curspec; //used in printing out debug info

    vector<Species*> sorted_species;  //Species sorted by max fit org in Species

//was 1.0*number_of_samples+1.0 for earlier results...
    float archive_thresh=(1.0*number_of_samples+1.0);// * 20.0 * envList.size(); //initial novelty threshold
    //if(!minimal_criteria)
    //	archive_thresh*=20;
//if(constraint_switch)
    //archive_thresh/=200.0;
    cout << "Archive threshold: " << archive_thresh << endl;
    //archive of novel behaviors
    noveltyarchive archive(archive_thresh,*maze_novelty_metric,true,push_back_size,minimal_criteria);

    data_rec Record; //stores run information

    int count=0;
    int pause;

    //Real-time evolution variables
    int offspring_count;
    Organism *new_org;

    //We try to keep the number of species constant at this number
    int num_species_target=NEAT::pop_size/20;

    //This is where we determine the frequency of compatibility threshold adjustment
    int compat_adjust_frequency = NEAT::pop_size/20;
    if (compat_adjust_frequency < 1)
        compat_adjust_frequency = 1;

    char sol_evo_fn[100];
    char sol_mod_fn[100];
    sprintf(sol_evo_fn,"%s_solution_evolvability.dat",output_dir);
    sprintf(sol_mod_fn,"%s_solution_modularity.dat",output_dir);

//activity stat log file
    char asfn[100];
    sprintf(asfn,"%s_activitystats.dat",output_dir);
    ofstream activity_stat_file(asfn);
    //Initially, we evaluate the whole population
    //Evaluate each organism on a test
    int indiv_counter=0;
    pop->evaluate_all();

    if (novelty) {
        //assign fitness scores based on novelty
        archive.evaluate_population(pop,true);
        //add to archive
        archive.evaluate_population(pop,false);
    }

    if (novelty && minimal_criteria)
        for (curorg=(pop->organisms).begin(); curorg!=(pop->organisms).end(); ++curorg)
        {
            if(!(*curorg)->noveltypoint->viable) {
                destroy_organism(*curorg);
            }
        }
//Get ready for real-time loop
    //Rank all the organisms from best to worst in each species
    pop->rank_within_species();

    //This average must be kept up-to-date by rtNEAT in order to select species probabailistically for reproduction
    pop->estimate_all_averages();

    cout <<"Entering real time loop..." << endl;

    //Now create offspring one at a time, testing each offspring,
    // and replacing the worst with the new offspring if its better
    for
    (offspring_count=0; offspring_count<NEAT::pop_size*1001; offspring_count++)
    {
//fix compat_threshold, so no speciation...
//      NEAT::compat_threshold = 1000000.0;
        //only continue past generation 1000 if not yet solved
        //if(offspring_count>=pop_size*1000 && firstflag)
        // if(firstflag)
        // break;

        int evolveupdate=6250;
        if (NEAT::evolvabilitytest && offspring_count % evolveupdate ==0) {
            char fn[100];
            char fn2[100];
            sprintf(fn,"%s_evolvability%d.dat",output_dir,offspring_count/evolveupdate);
            sprintf(fn,"%s_modularity%d.dat",output_dir,offspring_count/evolveupdate);
            for (curorg = (pop->organisms).begin(); curorg != pop->organisms.end(); ++curorg) {
                evolvability(*curorg,fn);
            }
        }


        //end of generation
        if (offspring_count % (NEAT::pop_size*1) == 0)
        {
            if ((offspring_count/NEAT::pop_size)%change_extinction_length==0)
                change_extinction_point();

            if (population_dirty) {
                pop->evaluate_all();
                population_dirty=false;
            }
            if (novelty) {
                archive.end_of_gen_steady(pop);
                //archive.add_randomly(pop);
                archive.evaluate_population(pop,false);
                cout << "ARCHIVE SIZE:" <<
                     archive.get_set_size() << endl;
            }
            double mx=0.0;
            double tot=0.0;
            Organism* b;
            for (curorg = (pop->organisms).begin(); curorg != pop->organisms.end(); ++curorg) {
                double fit = (*curorg)->noveltypoint->fitness;
                tot+=fit;
                if( fit > mx) {
                    mx=fit;
                    b=(*curorg);
                }
            }
            cout << "GEN" << offspring_count/NEAT::pop_size << " " << tot << " " << mx <<  endl;
            char fn[100];
            sprintf(fn,"%sdist%d",output_dir,offspring_count/NEAT::pop_size);
            if (NEAT::printdist)
                pop->print_distribution(fn);


#ifdef PLOT_ON11
            if(true) {
                best_fits.push_back(mx);
                fitness_plot.plot_data(best_fits,"lines","Fitness");


                vector<float> xc;
                vector<float> yc;
                vector<float> zc;
                for (curorg = (pop->organisms).begin(); curorg != pop->organisms.end(); ++curorg) {
                    int sz=(*curorg)->noveltypoint->data[0].size();
                    //xc.push_back((*curorg)->noveltypoint->data[0][sz-2]);
                    //yc.push_back((*curorg)->noveltypoint->data[0][sz-1]);
                    float _xc=(*curorg)->noveltypoint->data[0][sz-2];
                    float _yc=(*curorg)->noveltypoint->data[0][sz-1];
                    if((*curorg)->noveltypoint->viable) {
                        xc.push_back(_xc);
                        xc.push_back(_yc);
                    }
                    else {
                        zc.push_back(_xc);
                        zc.push_back(_yc);
                    }
                }
                for(int i=0; i<archive.get_set_size(); i++) {
                    noveltyitem *ni = archive.novel_items[i];
                    int sz=ni->data[0].size();
                    yc.push_back(ni->data[0][sz-2]);
                    yc.push_back(ni->data[0][sz-1]);
                }
                vector<vector <float> > blah;
                blah.push_back(xc);
                blah.push_back(yc);
                blah.push_back(zc);
                behavior_plot.plot_data_2d(blah);

            }
#endif


        }

        //write out current generation and fittest individuals
        if ( offspring_count % (NEAT::pop_size*NEAT::print_every) == 0 )
        {
            cout << offspring_count << endl;
            char fname[100];
            sprintf(fname,"%sarchive.dat",output_dir);
            archive.Serialize(fname);

            sprintf(fname,"%sfittest_%d",output_dir,offspring_count/NEAT::pop_size);
            archive.serialize_fittest(fname);

            sprintf(fname,"%sgen_%d",output_dir,offspring_count/NEAT::pop_size);
            pop->print_to_file_by_species(fname);


            sprintf(fname,"%srecord.dat",output_dir);
            Record.serialize(fname);
        }

        //Every pop_size reproductions, adjust the compat_thresh to better match the num_species_targer
        //and reassign the population to new species
        if (offspring_count % compat_adjust_frequency == 0) {
            count++;
#ifdef DEBUG_OUTPUT
            cout << "Adjusting..." << endl;
#endif
            if (novelty) {
                //update fittest individual list
                archive.update_fittest(pop);
                //refresh generation's novelty scores
                archive.evaluate_population(pop,true);
            }
            int num_species = pop->species.size();
            double compat_mod=0.1;  //Modify compat thresh to control speciation
            // This tinkers with the compatibility threshold
            if (num_species < num_species_target) {
                NEAT::compat_threshold -= compat_mod;
            }
            else if (num_species > num_species_target)
                NEAT::compat_threshold += compat_mod;

            if (NEAT::compat_threshold < 0.3)
                NEAT::compat_threshold = 0.3;
#ifdef DEBUG_OUTPUT
            cout<<"compat_thresh = "<<NEAT::compat_threshold<<endl;
#endif

            //Go through entire population, reassigning organisms to new species
            for (curorg = (pop->organisms).begin(); curorg != pop->organisms.end(); ++curorg) {
                pop->reassign_species(*curorg);
            }
        }


        //For printing only
#ifdef DEBUG_OUTPUT
        for (curspec=(pop->species).begin(); curspec!=(pop->species).end(); curspec++) {
            cout<<"Species "<<(*curspec)->id<<" size"<<(*curspec)->organisms.size()<<" average= "<<(*curspec)->average_est<<endl;
        }

        cout<<"Pop size: "<<pop->organisms.size()<<endl;
#endif

        //Here we call two rtNEAT calls:
        //1) choose_parent_species() decides which species should produce the next offspring
        //2) reproduce_one(...) creates a single offspring fromt the chosen species
        new_org=(pop->choose_parent_species())->reproduce_one(offspring_count,pop,pop->species);

        //Now we evaluate the new individual
        //Note that in a true real-time simulation, evaluation would be happening to all individuals at all times.
        //That is, this call would not appear here in a true online simulation.
#ifdef DEBUG_OUTPUT
        cout<<"Evaluating new baby: "<<endl;
#endif

        /*	data_record* newrec=new data_record();
        	newrec->indiv_number=indiv_counter;
        	//evaluate individual, get novelty point
        	new_org->noveltypoint =         communication_output=o3        communication_output=o3;;maze_novelty_map(new_org,newrec);
        	new_org->noveltypoint->indiv_number = indiv_counter;
        	new_org->fitness=new_org->noveltypoint->fitness;
        */
        data_record* newrec=new_org->datarec;
        //calculate novelty of new individual
        if (novelty) {
            archive.evaluate_individual(new_org,pop->organisms);
            //newrec->ToRec[5] = archive.get_threshold();
            newrec->ToRec[6] = archive.get_set_size();
            newrec->ToRec[RECSIZE-2] = new_org->noveltypoint->novelty;
        }
        if ( !new_org->noveltypoint->viable && minimal_criteria)
        {
            //new_org->fitness = SNUM/1000.0;
            //new_org->novelty = 0.00000001;
            //reset behavioral characterization
            //new_org->noveltypoint->reset_behavior();
            destroy_organism(new_org);
            //cout << "fail" << endl;
#ifdef DEBUG_OUTPUT
            cout << ":( " << endl;
#endif
        }
        else
        {
#ifdef DEBUG_OUTPUT
            cout << ":) " << new_org->noveltypoint->indiv_number << endl;
#endif
        }
        //add record of new indivdual to storage
        //Record.add_new(newrec);
        indiv_counter++;

        //update fittest list
        archive.update_fittest(new_org);
#ifdef DEBUG_OUTPUT
        cout << "Fitness: " << new_org->fitness << endl;
        cout << "Novelty: " << new_org->noveltypoint->novelty << endl;
        cout << "RFit: " << new_org->noveltypoint->fitness << endl;
#endif

        //Now we reestimate the baby's species' fitness
        new_org->species->estimate_average();

        //if solution, do evolvability

        if (newrec->ToRec[3]>=envList.size() && newrec->ToRec[4]>=envList.size()) {
            if (NEAT::evolvabilitytest)
            {
                cout << "solution found" << endl;
                evolvability(new_org,sol_evo_fn);
            }
        }


        if (!weakfirst && (newrec->ToRec[3]>=envList.size())) {
            weakfirst=true;
            //NEAT::evolvabilitytest=true; //TODO REMOVE LATER
            char filename[100];
            sprintf(filename,"%s_%d_weakfirst",output_dir,indiv_counter);
            new_org->print_to_file(filename);
            cout << "Maze weakly solved by indiv# " << indiv_counter << endl;
//disable quit for now
            if (fitness_measure == fitness_goal && false)
                firstflag=true;
        }
        //write out the first individual to solve maze
        if (!firstflag && (newrec->ToRec[3]>=envList.size() && newrec->ToRec[4]>=envList.size())) {

            //solution only when viable?
            if(new_org->noveltypoint->viable) {
                firstflag=true;
                char filename[100];
                sprintf(filename,"%s_%d_first",output_dir,indiv_counter);
                new_org->print_to_file(filename);
                //pop->print_to_file_by_species(filename);
                cout << "Maze solved by indiv# " << indiv_counter << endl;
                break;
            }
        }

        //Remove the worst organism
        if (rand_repl || fitness_measure ==fitness_rnd)
            pop->remove_random();
        else {
            pop->remove_worst();
        }

    }

    //write out run information, archive, and final generation
    cout << "COMPLETED...";
    char filename[100];
    sprintf(filename,"%srecord.dat",output_dir);
    char fname[100];
    sprintf(fname,"%srtarchive.dat",output_dir);
    archive.Serialize(fname);
    //Record.serialize(filename);

    sprintf(fname,"%sfittest_final",output_dir);
    archive.serialize_fittest(fname);

    sprintf(fname,"%srtgen_final",output_dir);
    pop->print_to_file_by_species(fname);
    delete pop;
    exit(0);
    return 0;
}

//initialize the maze simulation
Environment* mazesimIni(Environment* tocopy,Network *net, vector< vector<float> > &dc)
{
    double inputs[20];
    Environment *newenv= new Environment(*tocopy);

    //flush the neural net
    net->flush();
    //update the maze
    newenv->Update();
    //create neural net inputs
    newenv->generate_neural_inputs(inputs);
    //load into neural net

    net->load_sensors(inputs);

    //propogate input through net
    for (int i=0; i<10; i++)
        net->activate();

    return newenv;
}

//execute a timestep of the maze simulation evaluation
double mazesimStep(Environment* newenv,Network *net,vector< vector<float> > &dc)
{
    double inputs[20];

    newenv->generate_neural_inputs(inputs);
    net->load_sensors(inputs);
    net->activate();
    //use the net's outputs to change heading and velocity of navigator
    newenv->interpret_outputs(net->outputs[0]->activation,net->outputs[1]->activation,net->outputs[2]->activation);
    //update the environment
    newenv->Update();
    newenv->distance_to_poi();
    double dist = newenv->distance_to_target();
    if (dist<=1) dist=1;
    double fitness = 5.0/dist; //used for accumulated fitness (obselete)

    return fitness;
}


double mazesim(Network* net, vector< vector<float> > &dc, data_record *record,Environment* the_env,Organism* o=NULL,noveltyitem* ni=NULL)
{


    vector<float> data;

    int timesteps=the_env->steps; //simulated_timesteps;
    int stepsize=10000;

    double fitness=0.0;
    Environment *newenv;
    position_accumulator *accum;

    newenv=mazesimIni(the_env,net,dc);
    newenv->goalattract = goal_attract;
    //data collection vector initialization
    //dc.clear();

    if (novelty_measure == novelty_sample ||
            novelty_measure ==novelty_sample_free)
        data.reserve(timesteps/stepsize);
    if (novelty_measure == novelty_accum)
    {
        data.reserve(100);
        float minx,miny,maxx,maxy;
        newenv->get_range(minx,miny,maxx,maxy);
        vector<int> dims;
        dims.push_back(10);
        dims.push_back(10);
        accum=new position_accumulator(dims,minx,miny,maxx,maxy);
    }

    /*ENABLE FOR ADDT'L INFO STUDIES*/
    if (number_of_samples>0)
        stepsize=timesteps/number_of_samples;

    for (int i=0; i<timesteps; i++)
    {
        fitness+=mazesimStep(newenv,net,dc);
        //if taking additional samples, collect during run
        if (novelty_measure==novelty_sample ||
                novelty_measure==novelty_sample_free)
            if ((timesteps-i-1)%stepsize==0)
            {
                if(!newenv->hero.collide) {
                    data.push_back(newenv->hero.location.x);
                    data.push_back(newenv->hero.location.y);
                }
                else {
                    data.push_back(-10.0);
                    data.push_back(-10.0);
                }
            }

        float loc[2]= {newenv->hero.location.x,newenv->hero.location.y};
        if (novelty_measure==novelty_accum)
        {
            accum->add_point(loc);
        }
    }
   
   if(novelty_measure=novelty_outcome) {
    data.push_back(newenv->reachgoal);
    data.push_back(newenv->reachpoi);
   }
 
   the_env->communication_output=newenv->communication_output;

    if (extinction) {
        if (extinct(newenv->hero.location)) {
            if (o!=NULL) o->eliminate=true;
        }
    }
    if (fitness_measure == fitness_uniform)
        fitness = 1.0;
    //calculate fitness of individual as closeness to target
    if (fitness_measure == fitness_aoi) {
        fitness = -contained_dist(newenv->hero.location.x,newenv->hero.location.y);
    }

    if (fitness_measure == fitness_collgoal) {
        fitness=300 - newenv->distance_to_target();
        fitness-=newenv->hero.collisions/4.0;
        if (fitness<0.1) fitness=0.1;
    }

    if (fitness_measure == fitness_goal)
    {
        if(newenv->reachgoal) fitness=500.0f;
        else if(newenv->reachpoi) fitness=250.0f;
        else { 
          fitness=0.1;
           //fitness=300.0 - newenv->distance_to_target(); //was 500 for MCNS
          //double fit2=300.0 - newenv->distance_to_poi();
          
        }

        if (fitness<0.1) fitness=0.1;
        //if (newenv->hero.collide)
        //	fitness+=50;
    }
    if (fitness_measure == fitness_collisions)
    {
        fitness= (-newenv->hero.collisions);
    }
    if (fitness_measure == fitness_spin)
    {
        fitness=log(newenv->hero.total_spin+0.1);
        if (fitness>7) fitness=7.0;
        if (fitness<0) fitness=0.0;
        fitness=7.01-fitness;
    }

    if (fitness_measure ==fitness_rnd)
    {
        //todo assign random fitness, this needs to get reassigned
        //often...
        fitness = randint(10,100);
    }

    //calculate fitness as meeting minimal criteria
    if (fitness_measure == fitness_drift)
    {
        if (newenv->reachgoal)
        {
            fitness=1.0;
            if (newenv->reachpoi)
                fitness=500.0;
        }
        else
        {
            fitness=SNUM/1000.0;
        }
    }
    if (fitness_measure == fitness_reachone) {
        fitness=SNUM;
        float mod=500.00-newenv->closest_to_target;
        if(mod<0)
            mod=0;
        fitness+=mod;
    }

    if (fitness_measure == fitness_std)
    {
        fitness=SNUM;
        float mod = 500.0 - newenv->closest_to_target;
        if (mod<0) mod=0.0;
        float mod2 = 500.0 - newenv->closest_to_poi;
        if (mod2<0) mod2=0.0;

        fitness+=mod;
        fitness+=mod2;
        /*
                  if(newenv->reachgoal)
        		fitness+=250.0;
                  else
                        fitness+=mod;

                   if(newenv->reachpoi)
        		fitness+=250.0;
                   else if (newenv->reachgoal)
                        fitness+=mod2;
        */
    }

    //fitness as novelty studies
    //data.push_back(fitness);

    float x=newenv->hero.location.x;
    float y=newenv->hero.location.y;

    /* ENABLE FOR DISCRETIZATION STUDIES
    if(param>0)
    {
     long bins=powerof2(param);
     x=discretize(x,bins,0.0,200.0);
     y=discretize(y,bins,0.0,200.0);
    }
    */
    if (novelty_measure==novelty_fitness)
        data.push_back(fitness);
    if (novelty_measure==novelty_sample || novelty_measure==novelty_sample_free)
        if (false)
        {
            //novelty point is the ending location of the navigator
            data.push_back(x);
            data.push_back(y);
        }

    if (novelty_measure==novelty_accum)
    {
        accum->transform();
        for (int x=0; x<accum->size; x++)
            data.push_back(accum->buffer[x]);
    }

  if(ni!=NULL) {
  if(newenv->reachgoal)
	ni->solution=true;
    else
	ni->solution=false;

    the_env->get_range((ni->minx),(ni->miny),(ni->maxx),(ni->maxy)); 
    double xsz=ni->maxx-ni->minx;
    double ysz=ni->maxy-ni->miny;
    ni->max_dist = sqrt(xsz*xsz+ysz*ysz);
    ni->end_x=newenv->hero.location.x;
    ni->end_y=newenv->hero.location.y;
    ni->timesteps=newenv->steps;
    ni->collisions=newenv->hero.collisions;
    ni->tot_turn=newenv->hero.total_spin;
    ni->tot_dist=newenv->hero.total_dist;
    ni->end_goal_dist=newenv->distance_to_target(); 
    ni->closest_goal_dist=newenv->closest_to_target;
    ni->end_start_dist=newenv->distance_to_start();  

 }

    if (record!=NULL)
    {
        record->ToRec[0]+=fitness;
        record->ToRec[1]=newenv->hero.location.x;
        record->ToRec[2]=newenv->hero.location.y;
        record->ToRec[3]+=newenv->reachgoal;
        record->ToRec[4]+=newenv->reachpoi;
        record->ToRec[5]= (-newenv->hero.collisions);
    }

    if (novelty_measure==novelty_accum)
        delete accum;
    dc.push_back(data);

    delete newenv;
    return fitness;
}

float contained_dist(float x,float y) {
    if(contained(x,y)) return 0.0;
    float xd=0;
    float yd=0;
    if(x>200)
        xd=(x-200);
    else if(x<0)
        xd= -x;
    if(y>200)
        yd=(y-200);
    else if(y<0)
        yd = -y;
    return (xd*xd+yd*yd);
}

bool contained(float x,float y)
{
    Point p(x,y);
    if (x>200)
        return false;
    if (x<0)
        return false;
    if (y>200)
        return false;
    if (y<0)
        return false;

    return true;
    /*
    if(envList[0]->end.distance(p) < 400)
    {
     //cout <<"contained.." << endl;
     return true;
    }
    //cout <<"notcontained..." << endl;
    return false;
    */
}

void mutate_genome(Genome* new_genome,bool traits)
{
    Network* net_analogue;
    double mut_power=NEAT::weight_mut_power;
				double inno=0;
				int id=0;
    new_genome->mutate_link_weights(mut_power,1.0,GAUSSIAN);
    if(traits) {
        vector<Innovation*> innos;
        if (randfloat()<NEAT::mutate_add_node_prob)
            new_genome->mutate_add_node(innos,id,inno);
        else if (randfloat()<NEAT::mutate_add_link_prob) {
            //cout<<"mutate add link"<<endl;
            net_analogue=new_genome->genesis(0);
            new_genome->mutate_add_link(innos,inno,NEAT::newlink_tries);
            delete net_analogue;
        }


        if(randfloat()<0.05)
            new_genome->mutate_random_trait();
        if(randfloat()<0.05)
            new_genome->mutate_link_trait(1);
    }

    return;
}

#define MUTATIONS 200
void evolvability(Organism* org,char* fn,int* di,double* ev,bool recall) {
    bool solution=false;
    fstream file;
    file.open(fn,ios::app|ios::out);
    cout <<"Evolvability..." << endl;
// file << "---" <<  " " << org->winner << endl;
    double points[MUTATIONS*2];
    float minx,maxx,miny,maxy;
    envList[0]->get_range(minx,miny,maxx,maxy);
    double ox,oy,fit;
    int nodes;
    int connections;
    for (int i=0; i<MUTATIONS; i++) {
        Genome *new_gene= new Genome(*org->gnome);
        //new_org->gnome = new Genome(*org->gnome);
        if (i!=0) //first copy is clean
            for (int j=0; j<1; j++) mutate_genome(new_gene);
        Organism *new_org= new Organism(0.0,new_gene,0);

        noveltyitem* nov_item = maze_novelty_map(new_org);
        if (i==0) {
            fit=nov_item->fitness;
            nodes=new_org->net->nodecount();
            connections=new_org->net->linkcount();
            ox=nov_item->data[0][0];
            oy=nov_item->data[0][1];
        }
        if (nov_item->fitness>340) solution=true;
        if(recall) {
            for(int k=0; k<nov_item->data[0].size(); k++)
                file << nov_item->data[0][k] << " ";
            file << endl;
        }
        points[i*2]=nov_item->data[0][0];
        points[i*2+1]=nov_item->data[0][1];
        //HOW IT WAS:
        //points[i*2]=(nov_item->data[0][0]-minx)/(maxx-minx);
        //points[i*2+1]=(nov_item->data[0][1]-miny)/(maxy-miny);
        delete new_org;
        delete nov_item;
        //file << endl;
    }
    int dist = distinct(points,MUTATIONS,2);
    if (di!=NULL) *di=dist;
    double evol = 0.0; // test_indiv(points,MUTATIONS);
    if (ev!=NULL) *ev=evol;
    if(!recall)
        file << dist << " " << evol << " " << ox << " " << oy << " " << nodes << " " <<connections << " " << fit << " " << solution << endl;
    file.close();
    return;
}


void initialize_maze(const char* mazefile) {
NEAT::load_neat_params("neat.ne",true);
read_in_environments(mazefile,envList);
float minx,miny,maxx,maxy;
envList[0]->get_range(minx,miny,maxx,maxy);
cout << minx << " " << maxx << " " << miny << " " << maxy << endl;
}

//evaluates an individual and stores the novelty point
noveltyitem* maze_novelty_map(Organism *org,data_record* record)
{
    static int best = 0;
    noveltyitem *new_item = new noveltyitem;
    new_item->genotype=new Genome(*org->gnome);
    new_item->phenotype=new Network(*org->net);
    vector< vector<float> > gather;

    double fitness=0.0;
    static float highest_fitness=0.0;

    new_item->viable=true;

    gather.clear();
    if (record!=NULL) {
        record->ToRec[0]=0;
        record->ToRec[3]=0;
        record->ToRec[4]=0;
    }

    for (int x=0; x<envList.size(); x++)
       {

        if(x==0) envList[x]->communication_input=0.0;
        else envList[x]->communication_input = envList[x-1]->communication_output;

        org->eliminate=false;
        fitness+=mazesim(org->net,gather,record,envList[x],org,new_item);
  
        if(debugflag)
	cout << "ci" << envList[x]->communication_input << " " << "co" << envList[x]->communication_output << endl;
        
        if (org->eliminate) {
            new_item->viable=false;
            org->eliminate=false;
        }

        if(age_objective)
            new_item->secondary= -org->age;
        else
            new_item->secondary=fitness;
    }

    //minimal criteria handling code
    if (record!=NULL)
    {
        if (mc_no_collision)
        {
            if(record->ToRec[5] < 0)
                new_item->viable=false;
        }
        else if (area_of_interest)
        {
            if (!contained(record->ToRec[1],record->ToRec[2]))
            {
                new_item->viable=false;
            }
        }
        else if (mc_reach_onepoint)
            if ( record->ToRec[3]<envList.size())
            {
                new_item->viable=false;
            }
    }

    if (fitness>highest_fitness)
        highest_fitness=fitness;

    for (int i=0; i<gather.size(); i++)
        new_item->data.push_back(gather[i]);


  /*
   for (int x=0;x<gather.size();x++) 
   for(int y=0;y<gather[x].size();y++)
    cout << gather[x][y];
   cout <<endl;
  */

    //set fitness (this is 'real' objective-based fitness, not novelty)
    new_item->fitness=fitness;
    org->fitness=fitness;


    if(org->gnome->genes.size() > GENOME_SIZE_LIMIT) {
        new_item->viable=false;
        new_item->secondary=-1000000;
        destroy_organism(org);
    }

    return new_item;
}

population_state* create_maze_popstate(char* outputdir,const char* mazefile,int param,const char *genes, int gens,bool novelty) {

    maxgens=gens;
    float archive_thresh=3.0;
    noveltyarchive *archive= new noveltyarchive(archive_thresh,*maze_novelty_metric,true,push_back_size,minimal_criteria,true);

//if doing multiobjective, turn off speciation, TODO:maybe turn off elitism
    if (NEAT::multiobjective) NEAT::speciation=false;

    Population *pop;

    Genome *start_genome;
    char curword[20];
    int id;

    ostringstream *fnamebuf;
    int gen;

    if (!seed_mode)
        strcpy(seed_name,genes);
    if(seed_mode)
        cout << "READING IN SEED" << endl;
    ifstream iFile(seed_name,ios::in);

    read_in_environments(mazefile,envList);


    if (outputdir!=NULL) strcpy(output_dir,outputdir);
    cout<<"START GENERATIONAL MAZE EVOLUTION"<<endl;

    cout<<"Reading in the start genome"<<endl;
//Read in the start Genome
    iFile>>curword;
    iFile>>id;
    cout<<"Reading in Genome id "<<id<<endl;
    start_genome=new Genome(id,iFile);
    iFile.close();

    cout<<"Start Genome: "<<start_genome<<endl;

//Spawn the Population
    cout<<"Spawning Population off Genome"<<endl;
    cout << "Start genomes node: " << start_genome->nodes.size() << endl;
    if(!seed_mode)
        pop=new Population(start_genome,NEAT::pop_size);
    else
        pop=new Population(start_genome,NEAT::pop_size,0.0);
    cout<<"Verifying Spawned Pop"<<endl;
    pop->verify();

//set evaluator
    pop->set_evaluator(&maze_novelty_map);
    pop->evaluate_all();
    delete start_genome;
    return new population_state(pop,novelty,archive);
}

Population *maze_generational(char* outputdir,const char* mazefile,int param,const char *genes, int gens,bool novelty)
{
    char logname[100];
    sprintf(logname,"%s_log.txt",outputdir);
    logfile=new ofstream(logname);
    //pop->set_compatibility(&behavioral_compatibility);
    population_state* p_state = create_maze_popstate(outputdir,mazefile,param,genes,gens,novelty);

    for (int gen=0; gen<=maxgens; gen++)  { //WAS 1000
        cout<<"Generation "<<gen<<endl;
        if (gen%change_extinction_length==0)
            change_extinction_point();
        bool win = maze_generational_epoch(p_state,gen);
        p_state->pop->epoch(gen);

        if (win)
        {
            break;
        }

    }

    delete logfile;
    delete p_state;
    return NULL;
}

void destroy_organism(Organism* curorg) {
    curorg->fitness = SNUM/1000.0;
    curorg->noveltypoint->reset_behavior();
    curorg->destroy=true;
}

int maze_success_processing(population_state* pstate) {
    double& best_fitness = pstate->best_fitness;
    double& best_secondary = pstate->best_secondary;

    static bool win=false;
    static bool firstflag=false;
    static bool weakfirst=false;

    vector<Organism*>::iterator curorg;
    Population* pop = pstate->pop;
    //Evaluate each organism on a test
    int indiv_counter=0;
    for (curorg=(pop->organisms).begin(); curorg!=(pop->organisms).end(); ++curorg) {

        data_record* newrec = (*curorg)->datarec;
        if (!weakfirst && (newrec->ToRec[3]>=envList.size())) {
            weakfirst=true;
            char filename[100];
            cout << "Maze weakly solved by indiv# " << indiv_counter << endl;
//disable quit for now
        }


        //write out the first individual to solve maze
        if (!firstflag && (newrec->ToRec[3]>=envList.size() && newrec->ToRec[4]>=envList.size())) {
            if ((*curorg)->noveltypoint->secondary >best_secondary) {
                best_secondary=(*curorg)->noveltypoint->secondary;
                cout << "NEW BEST SEC " << best_secondary << endl;

            }


            if( (*curorg)->noveltypoint->viable) {
                //cout << (*curorg)->noveltypoint->viable << endl;

                cout << "Maze solved by indiv# " << indiv_counter << endl;
                cout << newrec->ToRec[5] << endl;
                //break;
                (*curorg)->winner=true;
                win=true;

                if (fitness_measure==fitness_goal) {
                    (*curorg)->winner=true;
                    win=true;
                    if ((*curorg)->noveltypoint->secondary >best_secondary) {
                        best_secondary=(*curorg)->noveltypoint->secondary;
                        cout << "NEW BEST SEC " << best_secondary << endl;

                    }
                }
            }
        }
        if ((*curorg)->noveltypoint->fitness > best_fitness)
        {
            best_fitness = (*curorg)->noveltypoint->fitness;
            //cout << "NEW BEST " << best_fitness << endl;
        }

        indiv_counter++;
        if ((*curorg)->noveltypoint->viable && !pstate->mc_met)
            pstate->mc_met=true;
        else if (pstate->novelty && !(*curorg)->noveltypoint->viable && minimal_criteria && pstate->mc_met)
        {
            destroy_organism((*curorg));
        }

        if (!pstate->novelty)
            (*curorg)->fitness = (*curorg)->noveltypoint->fitness;
    }

    if(logfile!=NULL)
        (*logfile) << pstate->generation*NEAT::pop_size<< " " << best_fitness << " " << best_secondary << endl;

    if (win && !firstflag)
    {
        for (curorg=(pop->organisms).begin(); curorg!=(pop->organisms).end(); ++curorg) {
            if ((*curorg)->winner) {
                cout<<"WINNER IS #"<<((*curorg)->gnome)->genome_id<<endl;
                char filename[100];
                sprintf(filename,"%s_%d_winner", output_dir,pstate->generation);
                (*curorg)->print_to_file(filename);
            }
        }
        firstflag=true;
    }
    if(win)
        return 1;
    return 0;
}

int maze_generational_epoch(population_state* pstate,int generation) {
    return
        generalized_generational_epoch(pstate,generation,&maze_success_processing);
}



int generalized_generational_epoch(population_state* pstate,int generation,successfunc success_processing) {
    pstate->generation++;

    bool novelty = pstate->novelty;
    noveltyarchive& archive = *pstate->archive;
    data_rec& Record = pstate->Record;
    Population **pop2 = &pstate->pop;
    Population* pop= *pop2;
    vector<Organism*>::iterator curorg,deadorg;
    vector<Species*>::iterator curspecies;
    vector<Organism*>& measure_pop=pstate->measure_pop;

    cout << "#GENOMES:" << Genome::increment_count(0) << endl;
    cout << "#GENES:" << Gene::increment_count(0) << endl;
    cout << "ARCHIVESIZE: " << archive.get_set_size() << endl;

    int evolveupdate=100;

    if (NEAT::multiobjective) {  //merge and filter population
        if(!novelty) NEAT::fitness_multiobjective=true;
        //if using alps-style aging
        if(pstate->max_age!=-1)
            for (curorg=(measure_pop.begin()); curorg!=measure_pop.end(); ++curorg) {
                (*curorg)->age++;
                //if too old, delete
                if((*curorg)->age > pstate->max_age) {
                    deadorg=curorg;
                    if(pstate->promote!=NULL) {
                        pstate->promote->measure_pop.push_back((*curorg));
                    }
                    else
                        delete (*curorg);
                    curorg=measure_pop.erase(deadorg);
                    curorg--;
                }
            }

        for (curorg=(pop->organisms).begin(); curorg!=(pop->organisms).end(); ++curorg) {
            measure_pop.push_back(new Organism(*(*curorg),true)); //TODO:maybe make a copy?
        }

        Genome* sg=pop->start_genome;
        evaluatorfunc ev=pop->evaluator;
        delete pop;
        pop=new Population(measure_pop);
        pop->start_genome=sg;
        pop->set_evaluator(ev);
        *pop2= pop;
    }

    if (NEAT::evolvabilitytest && generation%evolveupdate==0)
    {
        char fn[100];
        sprintf(fn,"%s_evolvability%d.dat",output_dir,generation/evolveupdate);
        for (curorg = (pop->organisms).begin(); curorg != pop->organisms.end(); ++curorg) {
            evolvability(*curorg,fn);
        }
    }

    int ret = success_processing(pstate);
    if(ret!=0)
        return 1;

    if (novelty)
    {

        archive.evaluate_population(pop,true);
        archive.evaluate_population(pop,false);

        pop->print_divtotal();


        for (curorg=(pop->organisms).begin(); curorg!=(pop->organisms).end(); ++curorg) {
            if ( !(*curorg)->noveltypoint->viable && minimal_criteria)
            {
                (*curorg)->fitness = SNUM/1000.0;
                (*curorg)->noveltypoint->fitness = SNUM/1000.0;
                (*curorg)->noveltypoint->novelty = SNUM/1000.0;
            }
        }
        //cout << "ARCHIVE SIZE:" << archive.get_set_size() << endl;
        //cout << "THRESHOLD:" << archive.get_threshold() << endl;
        archive.end_of_gen_steady(pop);
    }

    if (NEAT::multiobjective) {
        archive.rank(pop->organisms);

        if (pop->organisms.size()>NEAT::pop_size) {
            //chop population down by half (maybe delete orgs that aren't used)
            int start=NEAT::pop_size; //measure_pop.size()/2;
            vector<Organism*>::iterator it;
            for (it=pop->organisms.begin()+start; it!=pop->organisms.end(); it++) {
                (*it)->species->remove_org(*it);
                delete (*it);
            }
            pop->organisms.erase(pop->organisms.begin()+start,pop->organisms.end());
        }
    }



#ifdef PLOT_ON11
    if(true) {
        vector<float> x,y,z;
        pop->gather_objectives(&x,&y,&z);
        front_plot.plot_data(x,y,"p","Pareto front");
        //best_fits.push_back(pstate->best_fitness);
        //fitness_plot.plot_data(best_fits,"lines","Fitness");

        /*
        vector<float> xc;
        vector<float> yc;
            for (curorg = (pop->organisms).begin(); curorg != pop->organisms.end(); ++curorg) {
        	int sz=(*curorg)->noveltypoint->data[0].size();
            	//xc.push_back((*curorg)->noveltypoint->data[0][sz-2]);
        	//yc.push_back((*curorg)->noveltypoint->data[0][sz-1]);
        	if((*curorg)->noveltypoint->viable) {
            	xc.push_back((*curorg)->noveltypoint->data[0][sz-3]);
        	yc.push_back((*curorg)->noveltypoint->data[0][sz-2]);
        	}
        }
        behavior_plot.plot_data(xc,yc);

            }
        */
        vector<float> xc;
        vector<float> yc;
        float coltot=0.0;
        for (curorg = (pop->organisms).begin(); curorg != pop->organisms.end(); ++curorg) {

            coltot+=(*curorg)->datarec->ToRec[5];
            int sz=(*curorg)->noveltypoint->data[0].size();
            if((*curorg)->datarec->ToRec[5]>-5) {
                xc.push_back((*curorg)->noveltypoint->data[0][sz-2]);
                xc.push_back((*curorg)->noveltypoint->data[0][sz-1]);
            }
            else {
                yc.push_back((*curorg)->noveltypoint->data[0][sz-2]);
                yc.push_back((*curorg)->noveltypoint->data[0][sz-1]);
            }
        }
        cout << "COLTOT: " << coltot << endl;
        vector<vector <float> > blah;
        blah.push_back(xc);
        blah.push_back(yc);
        behavior_plot.plot_data_2d(blah);

    }
#endif


    char fn[100];
    sprintf(fn,"%sdist%d",output_dir,generation);
    if (NEAT::printdist)
        pop->print_distribution(fn);

    for (curspecies=(pop->species).begin(); curspecies!=(pop->species).end(); ++curspecies) {
        (*curspecies)->compute_average_fitness();
        (*curspecies)->compute_max_fitness();
    }

    //writing out stuff
    if ((generation+1)%NEAT::print_every == 0 )
    {
        char filename[100];
        sprintf(filename,"%s_record.dat",output_dir);
        char fname[100];
        sprintf(fname,"%s_archive.dat",output_dir);
        archive.Serialize(fname);
        sprintf(fname,"%sgen_%d",output_dir,generation);
        pop->print_to_file_by_species(fname);

        sprintf(fname,"%sfittest_%d",output_dir,generation);
        archive.serialize_fittest(fname);
    }

    if (NEAT::multiobjective) {
        for (curorg=measure_pop.begin(); curorg!=measure_pop.end(); curorg++) delete (*curorg);
        //clear the old population
        measure_pop.clear();
        if (generation!=maxgens)
            for (curorg=(pop->organisms).begin(); curorg!=(pop->organisms).end(); ++curorg) {
                measure_pop.push_back(new Organism(*(*curorg),true));
            }
    }

    //Create the next generation
    pop->print_avg_age();

    return 0;
}

