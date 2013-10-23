#include <iostream>
#include <fstream>
using namespace std;
#include <tclap/CmdLine.h>
#include <cstring>

#include <vector>
#include <unistd.h>
#include "neat.h"
#include "genome.h"
#include "population.h"
#include "experiments.h"
#include "alps.h"

using namespace TCLAP;
static bool biped=false;
CmdLine cmd("Maze evolution", ' ', "0.1");

int main(int argc, char **argv) {

//Parameter parsing code

    ValueArg<string> maze("m","maze","Maze file",false,"hard_maze_list.txt","string");
    cmd.add(maze);

    ValueArg<string> genes("z","sg","Starter genes",false,"mazestart_orig","string");
    cmd.add(genes);

    ValueArg<string> settings("s","settings","Settings file",false,"maze.ne","string");
    cmd.add(settings);

    ValueArg<string> output("o","output","Output directory",false,"./results","string");
    cmd.add(output);

    ValueArg<string> seed_genome("c","seed","Seed Genome",false,"","string");
    cmd.add(seed_genome);

    SwitchArg passive_switch("","passive","passive search",false);
    cmd.add(passive_switch);

    SwitchArg noveltySwitch("n","novelty","Enable novelty search",false);
    cmd.add(noveltySwitch);

    SwitchArg evaluateSwitch("","eval","Evaluate a genome",false);
    cmd.add(evaluateSwitch);

    SwitchArg generationalSwitch("","gen","Enable generational search",false);
    cmd.add(generationalSwitch);

    SwitchArg mcSwitch("","mc","Enable minimal criteria",false);
    cmd.add(mcSwitch);

    ValueArg<string> nov_measure("","nm","Novelty Measure",false,"std","string");
    cmd.add(nov_measure);

    ValueArg<string> fit_measure("f","fm","Fitness Measure",false,"goal","string");
    cmd.add(fit_measure);

    ValueArg<int> extra_param("p","parameter","Extra Parameter",false,0,"int");
    cmd.add(extra_param);

    ValueArg<int> num_samples("","samples","Num Samples",false,1,"int");
    cmd.add(num_samples);

    ValueArg<int> time_steps("","timesteps","Num Timesteps",false,400,"int");
    cmd.add(time_steps);

    ValueArg<int> generation_arg("","gens","Num generations",false,1000,"int");
    cmd.add(generation_arg);

    ValueArg<int> rng_seed("r","random_seed","Random Seed",false,-1,"int");
    cmd.add(rng_seed);

    ValueArg<long long> netindex("","ni","Net Index",false,0,"long int");


    //actually parse command line arguments
    cmd.add(netindex);
    cmd.parse(argc,argv);

    //these get overwritten by command line defaults above
    char mazename[100]="";
    char filename[100]="";
    char settingsname[100]="";
    char startgenes[100]="";

    NEAT::Population *p;

    int param = extra_param.getValue();
    int generations=generation_arg.getValue();

    //random seed
    srand( (unsigned)time( NULL )  + getpid());

    //unlesss you pass in a seed yourself (good for cluster runs)
    if(rng_seed.getValue()!=-1)
        srand((unsigned)rng_seed.getValue());


    strcpy(settingsname,settings.getValue().c_str());
    strcpy(mazename,maze.getValue().c_str());
    strcpy(filename,output.getValue().c_str());
    strcpy(startgenes,genes.getValue().c_str());


    //load in neat-specific parameter file
    NEAT::load_neat_params(settingsname,true);

    cout << "Maze: " << mazename << endl;
    cout << "Start genes: " << startgenes << endl;
    cout << "Generations: " << generations << endl;

    set_evaluate(evaluateSwitch.getValue());
    set_fit_measure(fit_measure.getValue());
    set_nov_measure(nov_measure.getValue());

    //how many timesteps should a maze simulation last?
    cout << "Timesteps: " << time_steps.getValue() << endl;
    set_timesteps(time_steps.getValue());

    //needed for novelty search maze runs 
    cout << "Num Samples: " << num_samples.getValue() << endl;
    set_samples(num_samples.getValue());

    set_seed(seed_genome.getValue());



    //needed for passive drift model, enumerating all behaviors in a particular space
    /*
    long long netindex_val=netindex.getValue();
    enumerate_behaviors(mazename,netindex_val,filename,param);
    return 0;
    */

    if(passive_switch.getValue()) {
        //for limited-capacity niche model
        p = maze_passive(filename,mazename,param,startgenes,noveltySwitch.getValue());
    }
    else if(!generationalSwitch.getValue())
    {
	//steady-state evolution
        cout << "NONGENERATIONAL" << endl;
        p = maze_novelty_realtime(filename,mazename,param,startgenes,noveltySwitch.getValue());
    }
    else
    {
	//generational evolution
        cout << "GENERATIONAL" << endl;
        p = maze_generational(filename,mazename,param,startgenes,generations,noveltySwitch.getValue());
    }

    return(0);

}
