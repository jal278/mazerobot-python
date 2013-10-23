#ifndef POPSTATE_H
#define POPSTATE_H
class population_state {
public:
    ~population_state() {
        clear_measure_pop();
        if(pop)
            delete pop;
        if(archive)
            delete archive;
    }

    population_state(Population* _pop,bool _n,noveltyarchive* _arc) {
        promote=NULL;
        evals=0;
        pop=_pop;
        novelty=_n;
        archive=_arc;
        best_fitness=0;
        max_age=-1;
        best_secondary = -100000.0;
        mc_met=false;
        generation=0;
    }

    bool mc_met;
    double best_fitness;
    double best_secondary;
    int max_age;
    int generation;
    long evals;
    noveltyarchive* archive;
    Population* pop;
    population_state* promote;
    data_rec Record;
    vector<Organism*> measure_pop;
    bool novelty;
    void reset() {
        mc_met=false;
        clear_measure_pop();
        archive->reset();
    }
    void clear_measure_pop() {
        vector<Organism*>::iterator curorg;
        for (curorg=measure_pop.begin(); curorg!=measure_pop.end(); curorg++) delete (*curorg);
        //clear the old population
        measure_pop.clear();
    }
};
#endif
