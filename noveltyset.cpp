#include "noveltyset.h"
#include <string.h>
#include "population.h"
#include "organism.h"

//for sorting by novelty
bool cmp(const noveltyitem *a, const noveltyitem* b)
{
    return a->novelty < b->novelty;
}

//for sorting by fitness
bool cmp_fit(const noveltyitem *a, const noveltyitem *b)
{
    return a->fitness < b->fitness;
}

noveltyitem::noveltyitem(const noveltyitem& item)
{
    added=false;
    //TODO: this might cause memory leak in
    //merge_population?
    age=item.age;
    viable=item.viable;
    genotype=new Genome(*(item.genotype));
    phenotype=new Network(*(item.phenotype));
    age=item.age;
    fitness=item.fitness;
    novelty=item.novelty;
    rank=item.rank;
    generation=item.generation;
    competition=item.competition;
    indiv_number=item.indiv_number;
    secondary=item.secondary;
    for(int i=0; i<(int)item.data.size(); i++)
    {
        vector<float> temp;
        for(int j=0; j<(int)item.data[i].size(); j++)
            temp.push_back(item.data[i][j]);
        data.push_back(temp);
    }

    minx=item.minx;
    miny=item.miny;
    maxx=item.maxx;
    maxy=item.maxy;

 
    end_x=item.end_x;
    end_y=item.end_y;
}

//merge two populations together according to novelty
Population* noveltyarchive::merge_populations(Population* p1, vector<Organism*> p2)
{

    vector<Organism*> total_orgs;
    vector<Organism*> merged_orgs;
    vector<Organism*>::iterator it;
    vector<noveltyitem*>::iterator novit;

//compile the organisms together
    for(it = p1->organisms.begin(); it!= p1->organisms.end(); it++)
    {
        total_orgs.push_back(*it);
        (*it)->blacklist=false;
    }

    for(it = p2.begin(); it!= p2.end(); it++)
    {
        total_orgs.push_back(*it);
        (*it)->blacklist=false;
    }

//throw in the archive as well

    for(novit = novel_items.begin(); novit != novel_items.end(); novit++)
    {
        //TODO: just creating these organisms will be a mem leak
        //eventually refactor...
        Organism* arch_org = new Organism(0.1,(*novit)->genotype,0,NULL);
        arch_org->noveltypoint = (*novit);
        arch_org->blacklist=false;
        total_orgs.push_back(arch_org);
        //or at least delete...?
    }

    int size = total_orgs.size(); //remove one since we are adding 1st
    cout << size << " " << p1->organisms.size() << " " << p2.size() << " " <<
         novel_items.size() << endl;

//randomly add first member to merged organisms
    Organism* last_added = total_orgs[rand()%size];
    last_added->blacklist=true;
    merged_orgs.push_back(last_added);

    for(it = total_orgs.begin(); it!=total_orgs.end(); it++)
    {
        (*it)->closest = 100000.0;
    }

//now greedily add point furthest from merged pop so far
//for(int x=0;x<(size/2)-1;x++)
    for(int x=0; x<(p1->organisms.size()-1); x++)
    {
        Organism* best=NULL;
        double best_dist= -1000.0;
        for(it = total_orgs.begin(); it!=total_orgs.end(); it++)
        {
            if ((*it)->blacklist)
                continue;

            double new_dist = (*novelty_metric)((*it)->noveltypoint,
                                                last_added->noveltypoint);

            if (new_dist < (*it)->closest)
                (*it)->closest = new_dist;

            if ((*it)->closest > best_dist)
            {
                best_dist = ((*it)->closest);
                best = *it;
            }
        }
        best->blacklist=true;
        last_added = best;
        merged_orgs.push_back(best);
    }

    return new Population(merged_orgs);


}

void noveltyarchive::rank(vector<Organism*>& orgs)
{
    evaluate_population(orgs); //assign novelty, local competition etc.
    int sz=orgs.size();

    //reset vars
    for(int i=0; i<sz; i++) {
        orgs[i]->noveltypoint->dominationcount=0;
        orgs[i]->noveltypoint->dominationList.clear();
    }

    //do domination
    for(int i=0; i<sz; i++)
        for(int j=0; j<sz; j++)
            orgs[i]->noveltypoint->dominate(orgs[j]->noveltypoint);

    int ranked=0;
    int cur_rank=0;

    //assign ranks
    vector<noveltyitem*> front;
    while(ranked!=sz) {
        for(int i=0; i<sz; i++)
        {
            if(orgs[i]->noveltypoint->dominationcount==0) {
                front.push_back(orgs[i]->noveltypoint);
                orgs[i]->noveltypoint->dominationcount = -1;
                orgs[i]->noveltypoint->rank=cur_rank;
                orgs[i]->fitness=sz-cur_rank;
                ranked++;
            }
        }

        //undominate those that the front dominated
        int frsz = front.size();
        for(int i=0; i<frsz; i++) {
            front[i]->undominate();
        }

        front.clear();
        cur_rank++;
    }
    int max_rank = cur_rank;

    for(int i=0; i<sz; i++)
        orgs[i]->fitness=max_rank-orgs[i]->noveltypoint->rank;
    //sort population based on rank
    std::sort(orgs.begin(), orgs.end(), order_orgs);


}
//evaluate the novelty of the whole population
void noveltyarchive::evaluate_population(Population* p1,vector<Organism*> p2,bool fitness)
{
    vector<Organism*>::iterator it;
    for(it=p1->organisms.begin(); it<p1->organisms.end(); it++)
        evaluate_individual((*it),p2,fitness);
}

//evaluate the novelty of the whole population
void noveltyarchive::evaluate_population(Population* pop,bool fitness)
{
    Population *p = (Population*)pop;
    vector<Organism*>::iterator it;
    for(it=p->organisms.begin(); it<p->organisms.end(); it++)
        evaluate_individual((*it),pop->organisms,fitness);
}

//evaluate the novelty of a list of organisms
void noveltyarchive::evaluate_population(vector<Organism*> orgs, bool fitness)
{
    vector<Organism*>::iterator it;
    for(it=orgs.begin(); it!=orgs.end(); it++)
        evaluate_individual((*it),orgs,fitness);
}

//evaluate the novelty of a single individual
void noveltyarchive::evaluate_individual(Organism* ind,vector<Organism*> pop,bool fitness)
{
    float result;
    if(fitness)  //assign fitness according to average novelty
    {
        if(ind->destroy)
        {
            result = 0.000000001;
            ind->fitness = result;
            ind->noveltypoint->novelty=result;
            ind->noveltypoint->genodiv=0;
        }
        else
        {
            if(!histogram)
                result = novelty_avg_nn(ind->noveltypoint,-1,false,&pop);
            else
                result = novelty_histogram(ind->noveltypoint);

        }
        //NEW WAY: production of novelty important
        if(production_score) {
            int init_weight=10;
            double fit_weight=init_weight;
            double fit_tot=ind->noveltypoint->novelty*init_weight;
            fit_tot+= ind->gnome->production;
            fit_weight+= ind->gnome->production_count;
            ind->fitness = fit_tot/fit_weight;
            //cout << fit_weight << endl;
            //cout << "adjusting novelty, weight " << fit_weight << ", from " << ind->noveltypoint->novelty << " to " << ind->fitness << endl;

            //END NEW WAY
        } else {
            ind->fitness = result;  //old way
        }
    }
    else  //consider adding a point to archive based on dist to nearest neighbor
    {
        if(!histogram)
        {
            result = novelty_avg_nn(ind->noveltypoint,1,false);
            //ind->noveltypoint->novelty=result;

            //if(!minimal_criteria)
            //   ind->noveltypoint->viable=true;
            if((!minimal_criteria || ind->noveltypoint->viable) && add_to_novelty_archive(result))
                add_novel_item(ind->noveltypoint);
        }
    }

}
