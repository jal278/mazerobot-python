#ifndef EXPERIMENTS_H
#define EXPERIMENTS_H
#include <iostream>
#include <iomanip>
#include <fstream>
#include <sstream>
#include <list>
#include <vector>
#include <algorithm>
#include <cmath>
#include <string>
#include "noveltyset.h"
#include "neat.h"
#include "network.h"
#include "population.h"
#include "organism.h"
#include "genome.h"
#include "species.h"
#include "datarec.h"
#include "maze.h"
#include "population_state.h"

using namespace std;
using namespace NEAT;

void initialize_maze(const char* mazefile);
void evolvability(Organism* org,char* fn,int *a=NULL,double* b=NULL,bool recall=false);
void enumerate_behaviors(const char* name,long long parm,const char* outname,int count);
void mutate_genome(Genome* new_genome,bool traits=false);

float contained_dist(float x,float y);
bool contained(float x,float y);
void set_debug_flag(bool val);
void set_age_objective(bool ao);
void set_evaluate(bool val);
void set_extinction(bool _ext);
void set_random_replace(bool val);
void  set_constraint_switch(bool val);
void set_aoi(bool val);
void set_nov_measure(string m);
void set_fit_measure(string m);

bool set_no_collision(bool no);
bool set_reach_onepoint(bool ro);
void set_mcmaze(string s);
void set_minimal_criteria(bool mc);
void set_samples(int s);
void set_timesteps(int s);
void set_seed(string s);
void set_goal_attract(bool s);
//generational maze experiments
Population *maze_passive(char* outputdir,const char* mazefile,int par,const char* genes,bool novelty);
Population *maze_alps(char* output_dir,const char* mazefile,int param, const char *genes, int gens, bool novelty);
Population *maze_generational(char* output_dir,const char* mazefile,int param, const char *genes, int gens, bool novelty);
typedef int (*successfunc)(population_state* ps);
typedef int (*epochfunc)(population_state* ps,int generation,successfunc sf);

int maze_generational_epoch(population_state *ps,int generation);
int maze_success_processing(population_state* pstate);
int generalized_generational_epoch(population_state* pstate,int generation,successfunc success_processing);
void destroy_organism(Organism* curorg);

//int maze_generational_epoch(Population **pop,int generation,data_rec& Record,noveltyarchive& archive,bool novelty);

int maze_novelty_realtime_loop(Population *pop,bool novelty=false);
Population *maze_novelty_realtime(char* output_dir=NULL,const char* mazefile="maze.txt",int param=-1,const char* genes=NULL,bool novelty=false);
noveltyitem* maze_novelty_map(Organism *org,data_record* record=NULL);

double mazesimStep(Environment* newenv,Network *net,vector< vector<float> > &dc);
Environment* mazesimIni(Environment* tocopy,Network *net, vector< vector<float> > &dc);

//Single pole balancing evolution routines ***************************
Population *pole1_test(int gens);
bool pole1_evaluate(Organism *org);
int pole1_epoch(Population *pop,int generation,char *filename);
int go_cart(Network *net,int max_steps,int thresh); //Run input
//Move the cart and pole
void cart_pole(int action, float *x,float *x_dot, float *theta, float *theta_dot);

//Double pole balacing evolution routines ***************************
class CartPole;

Population *pole2_test(int gens,int velocity);
bool pole2_evaluate(Organism *org,bool velocity,CartPole *thecart);
int pole2_epoch(Population *pop,int generation,char *filename,bool velocity, CartPole *thecart,int &champgenes,int &champnodes, int &winnernum, ofstream &oFile);

//rtNEAT validation with pole balancing *****************************
Population *pole2_test_realtime();
int pole2_realtime_loop(Population *pop, CartPole *thecart);


class CartPole {
public:
    CartPole(bool randomize,bool velocity);
    virtual void simplifyTask();
    virtual void nextTask();
    virtual double evalNet(Network *net,int thresh);
    double maxFitness;
    bool MARKOV;

    bool last_hundred;
    bool nmarkov_long;  //Flag that we are looking at the champ
    bool generalization_test;  //Flag we are testing champ's generalization

    double state[6];

    double jigglestep[1000];

protected:
    virtual void init(bool randomize);

private:

    void performAction(double output,int stepnum);
    void step(double action, double *state, double *derivs);
    void rk4(double f, double y[], double dydx[], double yout[]);
    bool outsideBounds();

    const static int NUM_INPUTS=7;
    const static double MUP = 0.000002;
    const static double MUC = 0.0005;
    const static double GRAVITY= -9.8;
    const static double MASSCART= 1.0;
    const static double MASSPOLE_1= 0.1;

    const static double LENGTH_1= 0.5;		  /* actually half the pole's length */

    const static double FORCE_MAG= 10.0;
    const static double TAU= 0.01;		  //seconds between state updates

    const static double one_degree= 0.0174532;	/* 2pi/360 */
    const static double six_degrees= 0.1047192;
    const static double twelve_degrees= 0.2094384;
    const static double fifteen_degrees= 0.2617993;
    const static double thirty_six_degrees= 0.628329;
    const static double fifty_degrees= 0.87266;

    double LENGTH_2;
    double MASSPOLE_2;
    double MIN_INC;
    double POLE_INC;
    double MASS_INC;

    //Queues used for Gruau's fitness which damps oscillations
    int balanced_sum;
    double cartpos_sum;
    double cartv_sum;
    double polepos_sum;
    double polev_sum;



};

#endif
