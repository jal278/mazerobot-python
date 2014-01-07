#ifndef ALPS_H
#define ALPS_H

#include "experiments.h"
#include "population.h"
#include "population_state.h"
#include "graph.h"
#include <iostream>
#include <fstream>
#define ALPS_MAX_LAYERS 10
class alps {

public:
    long evals;
    int generation;
    int scale;
    int max_layers;
    int clayers;
    int layer_ceiling;
    bool novelty;
    long maxevals;
    float best_fitness;
    int popsize;
    plot ageplot;
    plot fitnessplot;
    plot behaviorplot;
    plot paretoplot;
    noveltyarchive *protoarc;
    Genome* start_genome;
    population_state* layers[ALPS_MAX_LAYERS];
    evaluatorfunc evalf;
    const char* outname;
    ofstream* logfile;
    vector< vector< float > > age_record;
    vector< vector< float > > fitness_record;
    epochfunc generation_func;
    successfunc success_func;
    alps(int _layers, int _scale,Genome* sg,population_state* initial,successfunc sf, const char* outputdir,long _maxevals=1000000) {
        outname=outputdir;
        char logname[100];
        maxevals=_maxevals;
        sprintf(logname,"%s_log.txt",outputdir);
        logfile=new ofstream(logname);

        success_func = sf;
        best_fitness=0;
        start_genome =sg->duplicate(0);
        scale=_scale;
        max_layers=_layers;
        clayers=1;
        generation=0;
        novelty=initial->novelty;
        protoarc=new noveltyarchive(initial->archive);
        protoarc->neighbors=40;
        protoarc->localneighbors=40;
        evalf=initial->pop->evaluator;
        layers[0]=initial;
        layers[0]->max_age=scale;
        update_layer_cnt();
        evals=0;
        popsize=initial->pop->organisms.size();
        vector<float> k;
        age_record.push_back(k);
        fitness_record.push_back(k);
    }

    void update_layer_cnt(int k=-1) {
        if(k==-1)
         layer_ceiling = clayers*clayers*scale;
        else
         layer_ceiling = k*k*scale;
    }

    Organism* reproduce(population_state* from,population_state* to) {
        Organism* baby;
        Population::reproduce_simple(from->measure_pop,0,to->pop);
        return baby;
    }

    void reproduce_alps(population_state* r,population_state* bef,population_state* aft,int psize,bool onlybefore=false) {
        int added=0;
        bool first=true;
        r->pop->setclean(false);
        vector<Organism*> to_add;
        while(added<psize) {
            Organism* baby;
            if(first) {
             if(onlybefore) baby=bef->pop->species[0]->reproduce_champ(0,r->pop);
             else baby=r->pop->species[0]->reproduce_champ(0,r->pop);
             first=false;
            } else {  
              
            if(!onlybefore &&(bef==NULL || randfloat()<0.5)) {
                //cout << "cur";
                //baby=reproduce(r->pop->species[0],r);
                baby=r->pop->species[0]->reproduce_simple(0,r->pop);
            }
            else {
                //cout << "bef";
                //baby=reproduce(bef,r);
                baby=bef->pop->species[0]->reproduce_simple(0,r->pop);
            }
            }
            baby->clean=false;
            evals++;

            if(baby->age <= r->max_age) {
		//cout << "+" <<endl;
                added++;
                to_add.push_back(baby);
            }
            else
            {
		//cout << "-" <<endl;
                if(r->promote!=NULL)
                    r->promote->measure_pop.push_back(baby);
                else {
                    delete(baby);
                }
            }

        }
        for(vector<Organism*>::iterator it=to_add.begin(); it!=to_add.end(); it++) {
            r->pop->species[0]->add_Organism((*it));
            (*it)->species=r->pop->species[0];  //Point baby to its species
        }
        r->pop->rebuild();
    }

    void reproduce_layer(int i) {
        population_state *before=NULL, *after=NULL;
        if(i>0)
            before=layers[i-1];
        if(i<(clayers-1))
            after=layers[i+1];

        reproduce_alps(layers[i],before,after,popsize);
    }

    population_state* create_new_layer(int from_layer) {

        int psize=layers[clayers-1]->pop->organisms.size();

        noveltyarchive *new_arc =new noveltyarchive(protoarc);
        Population* new_pop=new Population(start_genome,1);
        new_pop->set_evaluator(evalf);

        population_state* np = new population_state(new_pop,novelty,new_arc);
        update_layer_cnt(clayers+1);
        np->max_age=layer_ceiling;
        reproduce_alps(np,layers[clayers-1],NULL,psize,true);
        np->pop->evaluate_all();
        cout << "POPSIZE: " << np->pop->organisms.size();
        cout << "NEWLAYERAGE:" << endl;
        np->pop->print_avg_age();

        evals+=np->pop->organisms.size();
        return np;

    }

    void repopulate(population_state* r) {

        int psize = r->pop->organisms.size();
        int added=0;

        while(added<psize) {
            Organism* baby;

            Genome* new_genome=start_genome->duplicate(added);
            //new_genome->mutate_link_weights(1.0,1.0,GAUSSIAN);
            new_genome->mutate_link_weights(2.0,1.0,COLDGAUSSIAN);
            new_genome->mutate_node_parameters(0.01,1.0,3.0,1.0,true);
            //new_genome->mutate_node_parameters(3.0,1.0,4.0,1.0,true);
            new_genome->randomize_traits();
            baby=new Organism(0.0,new_genome,1);
            r->pop->species[0]->add_Organism(baby);
            baby->species=r->pop->species[0];  //Point baby to its species
            added++;
        }
        r->pop->rebuild();
        r->pop->evaluate_all();
        evals+=r->pop->organisms.size();
        r->reset();
    }


    void do_alps() {
        bool success=false;
        while(!success && evals<maxevals) {
            cout << "alps generation " << generation << endl;
            cout << "layers " << clayers << " ceiling" << layer_ceiling << endl;
//reproduce layers
            for(int i=0; i<clayers; i++) {
                layers[i]->best_fitness = 0;
                layers[i]->evals=evals;
                success=generalized_generational_epoch(layers[i],generation,success_func);
                if (success) {
                    cout <<"SUCCESS" << endl;
                    break;
                }
                age_record[i].push_back(layers[i]->pop->avgage);
                fitness_record[i].push_back(layers[i]->best_fitness);
                if(layers[i]->best_fitness > best_fitness)
                    best_fitness=layers[i]->best_fitness;
                reproduce_layer(i);
                //layers[i]->archive->increment_age(layers[i]->max_age);
                cout << "Layer " << i << ":" << layers[i]->mc_met << endl;
                cout << "evals: " << evals << " f: " << layers[i]->best_fitness << endl;
            }
            (*logfile) << evals << " " << best_fitness << endl;

            vector< vector< float > > pareto;
            vector< vector< float > > behaviors;
            for(int i=0; i<clayers; i++) {
                vector<Organism*>::iterator org;
                vector<float> collect;
                vector<float> pcollect;
                for(org=layers[i]->measure_pop.begin(); org!=layers[i]->measure_pop.end(); org++)
                {
                    int sz=(*org)->noveltypoint->data[0].size();
                    collect.push_back((*org)->noveltypoint->data[0][sz-2]);
                    collect.push_back((*org)->noveltypoint->data[0][sz-1]);
                    pcollect.push_back((*org)->noveltypoint->novelty);
                    pcollect.push_back((*org)->noveltypoint->genodiv);
                }
                pareto.push_back(pcollect);
                behaviors.push_back(collect);
            }
#ifdef PLOT_ON
            paretoplot.plot_data_2d(pareto);
            behaviorplot.plot_data_2d(behaviors);
            //ageplot.plot_data(age_record,"lines");
            //fitnessplot.plot_data(fitness_record,"lines");
#endif

            //if time to add new layer, create if from previous layer
            if(clayers<max_layers && ((generation+1)==layer_ceiling)) {
                cout << "Adding layer " << clayers << endl;
                //create new layer, set age limit, etc
                layers[clayers]=create_new_layer(clayers);
                layers[clayers-1]->promote=layers[clayers];
                clayers++;
                update_layer_cnt();
                if(clayers==(max_layers))
                    layers[clayers-1]->max_age=10000000;
                else
 		    layers[clayers-1]->max_age=layer_ceiling;
                vector<float> k;
                age_record.push_back(k);
                fitness_record.push_back(k);
             
            }

            //if multiple of scale, recreate first layer from start genome
            if((generation+1)%scale==0) {
                cout << "regenerating first layer" << endl;
                repopulate(layers[0]);
            }

            generation++;
        }
    }
};
#endif
