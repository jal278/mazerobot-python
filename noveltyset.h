#ifndef NVSET_H
#define NVSET_H

//#define PLOT_ON

#include <math.h>
#include <vector>
#include <utility>
#include <iostream>
#include <sstream>
#include <fstream>
#include <algorithm>
#include <cstdlib>

#include "population.h"
#include "neat.h"

#define SNUM 0.0000001

#define ARCHIVE_SEED_AMOUNT 1
bool get_age_objective();
inline float scale(float lo, float hi, float x)
{
    if (x<lo)
        return 0;
    if (x>hi)
        return 1;
    return (x-lo)/(hi-lo);
}

using namespace std;
using namespace NEAT;

class histogram_accumulator
{
public:
    long count;
    int *buffer;
    vector<int> dim;

    histogram_accumulator(vector<int> dims)
    {
        count=0;
        dim=dims;
        long size=1;
        for (int x=0; x<dim.size(); x++)
            size*=dim[x];
        buffer=(int*)malloc(sizeof(int)*size);
    }

    double query_point(float* v,bool increment=true)
    {
        long int index=0;
        long int multiplier=1;
        for (int x=0; x<dim.size(); x++)
        {
            int loc_index = v[x] * dim[x];
            index+=multiplier*loc_index;
            multiplier*=dim[x];
        }

//double novelty = 1.0-((double)buffer[index]) / (double)count;
        double novelty = 1.0/((double)buffer[index]+1);

        if (increment)
        {
            buffer[index]++;
            count++;
        }

        return novelty;

    }

    ~histogram_accumulator()
    {
        free(buffer);
    }

};

class histogram_multiple
{
public:
    vector<histogram_accumulator*> accums;

    histogram_multiple(vector< vector< int> > dims)
    {
        for (int x=0; x<dims.size(); x++)
            accums.push_back(new histogram_accumulator(dims[x]));
    }

    ~histogram_multiple()
    {
        for (int x=0; x<accums.size(); x++)
            delete accums[x];
    }

    double query_point(float* v,bool increment=true)
    {
        int cnt=0;
        double prob=1.0;
        for (int x=0; x<accums.size(); x++)
        {
            double temp_prob = accums[x]->query_point(v+cnt,increment);
//cout << temp_prob << " ";
            prob*=temp_prob;
        }
//cout << endl;
        return prob;
    }

};

//a novelty item is a "stake in the ground" i.e. a novel phenotype
class noveltyitem
{
public:
    bool added;
    bool viable;
    bool solution;
    int indiv_number;
 
    int num_samps;
    int timesteps;

    double end_goal_dist;
    double end_start_dist;
    double closest_goal_dist;

    double tot_dist;
    double tot_turn;
    double collisions;

    double end_x;
    double end_y;
    double mid_x;
    double mid_y;
    float maxx;
    float minx;
    float maxy;
    float miny;
    float max_dist;
//we can keep track of genotype & phenotype of novel item
    NEAT::Genome* genotype;
    NEAT::Network* phenotype;

//used to collect data
    vector< vector<float> > data;

//future use
    int age;
//used for analysis purposes
    float novelty_scale;
    float novelty;
    float fitness;
    float secondary;
    float generation;
    float genodiv;
    int competition;
    int rank;
    bool ranked;
    int dominationcount;

    vector< noveltyitem* > dominationList;
    void undominate() {
        for(int i=0; i<dominationList.size(); i++) {
            dominationList[i]->dominationcount--;
        }
        dominationList.clear();
    }

    void dominate(noveltyitem* k) {
        if(dominates(k)) {
            k->dominationcount++;
            dominationList.push_back(k);
        }
    }

    bool dominates(noveltyitem*k) {
        if(NEAT::fitness_multiobjective) return dominates_fitness(k);
        if(NEAT::local_competition) return dominates_local(k);
        return dominates_global(k);
    }

#define GDTHRESH 20.0
    bool dominates_fitness(noveltyitem* k) {
        if (NEAT::mo_speciation && secondary < k->secondary || fitness < k->fitness
                || genodiv+GDTHRESH < k->genodiv)
            return false;
        if (secondary > k->secondary || fitness > k->fitness)
            //	|| genodiv > k->genodiv+GDTHRESH)
            return true;

        return false;
    }
    bool dominates_global(noveltyitem* k) {
        if (NEAT::mo_speciation && secondary < k->secondary || novelty < k->novelty
                || genodiv+GDTHRESH < k->genodiv)
            return false;
        if (secondary > k->secondary || novelty > k->novelty)
            //	|| genodiv > k->genodiv+GDTHRESH)
            return true;

        return false;
    }

    bool dominates_local(noveltyitem* k) {
        if (NEAT::mo_speciation && competition < k->competition || novelty < k->novelty
                || genodiv+GDTHRESH < k->genodiv)
            return false;
        if (competition > k->competition || novelty > k->novelty)
            //|| genodiv > k->genodiv+GDTHRESH)
            return true;

        return false;
    }

//this will write a novelty item to file

    void reset_behavior()
    {
        for(int x=0; x<data.size(); x++)
            for(int y=0; y<data[x].size(); y++)
                data[x][y]=0.0;
    }

    bool Serialize(ofstream& ofile)
    {
        genotype->print_to_file(ofile);
        SerializeNoveltyPoint(ofile);
        return true;
    }

//serialize the novelty point itself to file
    bool SerializeNoveltyPoint(ofstream& ofile)
    {
        ofile << "/* Novelty: " << novelty << " Fitness: " << fitness << " Generation: " << generation << " Indiv: " << indiv_number << " */" << endl;
        ofile << "/* Point:";
        for (int i=0; i<(int)data.size(); i++)
            for (int j=0; j<(int)data[i].size(); j++)
                ofile << " " << data[i][j];
        ofile << " */" << endl;
        return true;
    }


    noveltyitem(const noveltyitem& item);
//initialize...
    noveltyitem()
    {
        viable=true;
        novelty_scale=1.0;
        added=false;
        genotype=NULL;
        phenotype=NULL;
        age=0;
        secondary=-1000000.0;
        genodiv=0.0;
        generation=0.0;
        indiv_number=(-1);
        solution=false;
    }

    ~noveltyitem()
    {
        if (genotype)
            delete genotype;
        if (phenotype)
            delete phenotype;

    }


};

//different comparison functions used for sorting
bool cmp(const noveltyitem *a, const noveltyitem *b);
bool cmp_fit(const noveltyitem *a, const noveltyitem *b);


//the novelty archive contains all of the novel items we have encountered thus far
//Using a novelty metric we can determine how novel a new item is compared to everything
//currently in the novelty set
class noveltyarchive
{

public:
    histogram_multiple* hist;
    bool histogram;
    bool production_score;
    //are we collecting data?
    bool record;

    //are we doing mc ns?
    bool minimal_criteria;
    bool minimal_criteria_met;
    ofstream *datafile;
    ofstream *novelfile;
    typedef pair<float, noveltyitem*> sort_pair;
    //all the novel items we have found so far
    vector<noveltyitem*> novel_items;
    vector<noveltyitem*> fittest;

    //current generation novelty items
    vector<noveltyitem*> current_gen;

    //novel items waiting addition to the set pending the end of the generation
    vector<noveltyitem*> add_queue;
    //the measure of novelty
    float (*novelty_metric)(noveltyitem*,noveltyitem*);
    //minimum threshold for a "novel item"
    float novelty_threshold;
    float novelty_floor;
    //counter to keep track of how many gens since we've added to the archive
    int time_out;
    //parameter for how many neighbors to look at for N-nearest neighbor distance novelty
    int neighbors;
    int localneighbors;
    //radius for SOG-type (not currently used)
    float radius;
    int this_gen_index;

    //hall of fame mode, add an item each generation regardless of threshold
    bool hall_of_fame;
    //add new items according to threshold
    bool threshold_add;
    bool generational;
    bool local_competition;
    //current generation
    int generation;
public:
    noveltyarchive(noveltyarchive* mimic) {

        constructor(mimic->novelty_threshold,mimic->novelty_metric,mimic->record,-1,mimic->minimal_criteria,mimic->generational);
    }

    noveltyarchive(float threshold,float (*nm)(noveltyitem*,noveltyitem*),bool rec=true,int pbs=-1,bool mc=false,bool _generational=false) {
        constructor(threshold,nm,rec,pbs,mc,generational);
    }
    void constructor(float threshold,float (*nm)(noveltyitem*,noveltyitem*),bool rec=true,int pbs=-1,bool mc=false,bool _generational=false)
    {
        minimal_criteria_met=false;
        production_score=NEAT::production;
        //how many nearest neighbors to consider for calculating novelty score?
        //histogram adds
        local_competition=NEAT::local_competition;
        histogram=false;
        generational=_generational;
        minimal_criteria=mc;
        vector< vector<int> > k;
        vector< int> l;

        if (pbs==-1)
        {
            histogram=false;
            pbs=5;
        }
        l.push_back(pbs);
        l.push_back(pbs);
        for (int x=0; x<1; x++)
            k.push_back(l);

        hist = new histogram_multiple(k);

        neighbors=15; //was 15
        localneighbors=15;

        generation=0;
        time_out=0; //used for adaptive threshold
        novelty_threshold=threshold;
        novelty_metric=nm; //set the novelty metric via function pointer
        novelty_floor=0.1; //lowest threshold is allowed to get
        record=rec;
        this_gen_index=ARCHIVE_SEED_AMOUNT;
        hall_of_fame=false;
        threshold_add=true;

        if (record)
        {
            datafile = new ofstream("runresults.dat");
        }
    }

    ~noveltyarchive()
    {
        if (record)
        {
            datafile->close();
        }
        vector<noveltyitem*>::iterator it;
        for(it=novel_items.begin(); it!=novel_items.end(); it++)
            delete (*it);
        for(it=fittest.begin(); it!=fittest.end(); it++)
            delete (*it);
        //probably want to delete all the noveltyitems at this point
    }
    void increment_age(int maxage) {
        vector<noveltyitem*>::iterator it,deadit;
        for(it=novel_items.begin(); it!=novel_items.end(); it++) {
            (*it)->age++;
            if( (*it)->age>maxage) {
                delete (*it);
                it=novel_items.erase(it);
                it--;
            }

        }
    }
    void reset() {
        vector<noveltyitem*>::iterator it;
        for(it=novel_items.begin(); it!=novel_items.end(); it++)
            delete (*it);
        novel_items.clear();
    }
public:


    float get_threshold() {
        return novelty_threshold;
    }
    int get_set_size()
    {
        return (int)novel_items.size();
    }

    //add novel item to archive
    void add_novel_item(noveltyitem* item,bool aq=true)
    {
        if (histogram)
            return;
        /*
                item->added=true;
                item->generation=generation;
        */
        novel_items.push_back(new noveltyitem(*item));
        if (aq)
            add_queue.push_back(item);
    }

#define MIN_ACCEPTABLE_NOVELTY 0.005
    //not currently used
    void add_randomly(Population* pop)
    {
        for (int i=0; i<(int)pop->organisms.size(); i++)
        {
            if (((float)rand()/RAND_MAX)<(0.0005))
            {
                noveltyitem* newitem = new noveltyitem(*pop->organisms[i]->noveltypoint);
                if (newitem->novelty > MIN_ACCEPTABLE_NOVELTY)
                    add_novel_item(newitem,false);
                else delete newitem;
            }
        }
    }

    noveltyitem *get_item(int i) {
        return novel_items[i];
    }
    void rank(vector<Organism*>& orgs);
    //merge two populations into one
    Population* merge_populations(Population* p1, vector<Organism*> p2);
    //evaluate group of organisms against each other
    void evaluate_population(vector<Organism*> orgs, bool fitness=true);
    //evaluate one pop in terms of another (generational ns)
    void evaluate_population(Population* to_eval, vector<Organism*> against,bool fitness=true);
    //re-evaluate entire population for novelty
    void evaluate_population(Population* pop,bool fitness=true);
    //evaluate single individual for novelty
    void evaluate_individual(Organism* individual,vector<Organism*> pop,bool fitness=true);
    void evaluate_individual(Organism* individual,Population *pop, bool fitness=true) {
        evaluate_individual(individual,pop->organisms,fitness);
    }

    //maintain list of fittest organisms so far
    void update_fittest(Organism* org)
    {
        int allowed_size=5;
        if ((int)fittest.size()<allowed_size)
        {
            if (org->noveltypoint!=NULL)
            {
                noveltyitem* x = new noveltyitem(*(org->noveltypoint));
                fittest.push_back(x);
                sort(fittest.begin(),fittest.end(),cmp_fit);
                reverse(fittest.begin(),fittest.end());
            }
            else
            {
                cout<<"WHY NULL?" << endl;
            }
        }
        else
        {
            if (org->noveltypoint->fitness > fittest.back()->fitness)
            {
                noveltyitem* x = new noveltyitem(*(org->noveltypoint));
                fittest.push_back(x);

                sort(fittest.begin(),fittest.end(),cmp_fit);
                reverse(fittest.begin(),fittest.end());

                delete fittest.back();
                fittest.pop_back();

            }
        }
    }

    //resort fittest list
    void update_fittest(Population* pop)
    {

        sort(fittest.begin(),fittest.end(),cmp_fit);
        reverse(fittest.begin(),fittest.end());

    }

    //write out fittest list
    void serialize_fittest(char *fn)
    {
        ofstream outfile(fn);
        for (int i=0; i<(int)fittest.size(); i++)
            fittest[i]->Serialize(outfile);
        outfile.close();
    }

    //adjust dynamic novelty threshold depending on how many have been added to
    //archive recently
    void add_pending()
    {
        if (record)
        {
            (*datafile) << novelty_threshold << " " << add_queue.size() << endl;
        }

        if (hall_of_fame)
        {
            if (add_queue.size()==1) time_out++;
            else time_out=0;
        }
        else
        {
            if (add_queue.size()==0)	time_out++;
            else time_out=0;
        }

        //if no individuals have been added for 10 generations
        //lower threshold
        if (time_out==10) {
            novelty_threshold*=0.95;
            if (novelty_threshold<novelty_floor)
                novelty_threshold=novelty_floor;
            time_out=0;
        }

        //if more than four individuals added this generation
        //raise threshold
        if (add_queue.size()>4) novelty_threshold*=1.2;

        add_queue.clear();

        this_gen_index = novel_items.size();
    }

    //criteria for adding to the archive
    bool add_to_novelty_archive(float novelty)
    {

        if (NEAT::archive && ((float)rand()/RAND_MAX)<(0.001))
            return true;
        return false;

        /*
          if (novelty>novelty_threshold)
              return true;
          else
              return false;
          */
    }

    //steady-state end of generation call (every so many indivudals)
    void end_of_gen_steady(Population* pop,int maxage=-1)
    {

        generation++;

        add_pending();
    }

    float novelty_histogram(noveltyitem* item)
    {
        float data[30];
        for (int x=0; x<2; x++)
            data[x]=scale(0,200,item->data[0][x]);
        return hist->query_point(data);
    }

    float diversity_avg_nn(noveltyitem* item,vector<Organism*> *pop) {
        vector<sort_pair> diversities;
        for(int i=0; i<pop->size(); i++)
            diversities.push_back(make_pair((*pop)[i]->gnome->compatibility(item->genotype), (*pop)[i]->noveltypoint));
        sort(diversities.begin(),diversities.end());
        float sum=0.0f;
        for(int i=0; i<neighbors; i++) {
            sum+=diversities[i].first;
        }
        return sum/neighbors;
    }

    //nearest neighbor novelty score calculation
    float novelty_avg_nn(noveltyitem* item,int neigh=-1,bool ageSmooth=false,vector<Organism*> *pop=NULL)
    {
        vector<sort_pair> novelties;
        if (pop)
            novelties = map_novelty_pop(novelty_metric,item,*pop);
        else
            novelties = map_novelty(novelty_metric,item);
        sort(novelties.begin(),novelties.end());

        float density=0.0;
        int len=novelties.size();
        float sum=0.0;
        float weight=0.0;


        if (neigh==-1)
        {
            neigh=neighbors;
            item->competition=0;
        }
        if (len<ARCHIVE_SEED_AMOUNT && NEAT::archive)
        {
            add_novel_item(item);
        }
        else
        {
            len=neigh;
            if ((int)novelties.size()<len)
                len=novelties.size();
            int i=0;

            while (weight<neigh && i<(int)novelties.size())
            {
                float term = novelties[i].first;
                float w = 1.0;

                sum+=term*w;
                weight+=w;

                if (weight<localneighbors && neigh!=1) {
                    if(novelties[i].second->secondary < item->secondary)
                        item->competition++;
                    //sum+=5.0f;
                }

                i++;
            }

            if (weight!=0)
            {
                density = sum/weight;
            }
        }
        if(density <SNUM*100)
        {
            density=SNUM*100; // + (((float)rand()/RAND_MAX)*SNUM);
        }
        //genotypic diversity
        if(pop!=NULL)
        {
            item->genodiv=diversity_avg_nn(item,pop);
        }
        //genotypic
        if(neigh!=1)
            item->novelty=density;
        item->generation=generation;
        return density;
    }

    //fitness = avg distance to k-nn in novelty space
    float test_fitness(noveltyitem* item)
    {
        if (!histogram)
            return novelty_avg_nn(item,-1,false);
        else
        {
            float val = novelty_histogram(item);
            cout << val << endl;
            return val;
        }
    }

    float test_novelty(noveltyitem* item)
    {
        if (!histogram)
            return novelty_avg_nn(item,1,false);
        else
        {
            float val = novelty_histogram(item);
            cout << val << endl;
            return val;
        }
    }

    //map the novelty metric across the archive
    vector<sort_pair> map_novelty(float (*nov_func)(noveltyitem*,noveltyitem*),noveltyitem* newitem)
    {
        vector<sort_pair> novelties;
        for (int i=0; i<(int)novel_items.size(); i++)
        {
            novelties.push_back(make_pair((*novelty_metric)(novel_items[i],newitem),novel_items[i]));
        }
        return novelties;
    }

    //map the novelty metric across the archive + current population
    vector<sort_pair> map_novelty_pop(float (*nov_func)(noveltyitem*,noveltyitem*),noveltyitem* newitem, vector<Organism*> pop)
    {
        vector<sort_pair> novelties;

        for (int i=0; i<(int)novel_items.size(); i++)
        {
            novelties.push_back(make_pair((*novelty_metric)(novel_items[i],newitem),novel_items[i]));
        }
        for (int i=0; i<(int)pop.size(); i++)
        {
            novelties.push_back(make_pair((*novelty_metric)(pop[i]->noveltypoint,newitem), pop[i]->noveltypoint));
        }
        return novelties;
    }

    //write out archive
    bool Serialize(char* fname)
    {
        ofstream outfile;
        outfile.open(fname);
        if (!outfile) {
            perror ("The following error occurred");
            std::cerr<<"Can't open "<<fname<<" for output"<<std::endl;
            return false;
        }
        bool res= Serialize(outfile);
        outfile.close();
        return res;
    }

    //write out archive
    bool Serialize(ofstream& ofile)
    {
        for (int i=0; i<(int)novel_items.size(); i++)
        {
            novel_items[i]->Serialize(ofile);
        }
        return true;
    }

};


#endif
