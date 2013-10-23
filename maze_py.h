#include "experiments.h"
#include "noveltyset.h"
#include "genome.h"

class mazenav {
 public:

  static void seed(int sd) {
  srand ( sd );
 }

 static void random_seed() {
  srand ( time(NULL) );
 }

  Genome *g;
  Organism *o;
  noveltyitem* nov_item;
  bool rendered;
  mazenav() {
	g=NULL;
	o=NULL;
	nov_item=NULL;
	rendered=false;
  }
  int complexity() {
   return g->genes.size();
  }

  double distance(mazenav* other) {
   return g->compatibility(other->g);
  }

  mazenav* copy() {
    mazenav* ret = new mazenav();
    ret->g = g->duplicate(0);
    return ret;
  }
 
  void save(const char *fname) {
   g->print_to_filename(fname);
  }

  void load_new(const char *fname) {
   g = Genome::new_Genome_load(fname);
  }

  static void initmaze(const char* mazefile) {
   initialize_maze(mazefile);
  }

  void init_rand() {
	g=new Genome(11,2,0,0);
  }

  void make_random() {
         int new_nodes = randint(0,6);
         int new_links = randint(0,10);
 
 	std::vector<Innovation*> innovs;
 	//todo:make these global if you want to use recombination
        int curnode_id=100;
        double curinnov=1000.0;
	init_rand();
         for(int k=0;k<new_nodes;k++)       
		 g->mutate_add_node(innovs,curnode_id,curinnov);
         for(int k=0;k<new_links;k++) {
				Network* net_analogue=g->genesis(0);
				g->mutate_add_link(innovs,curinnov,NEAT::newlink_tries); 
				delete net_analogue;
 	}
	g->mutate_link_weights(2.0,1.0,COLDGAUSSIAN);
  }

  void mutate() {
	mutate_genome(g,true);
  }
 
  void map() {
   o=new Organism(0.0,g,0);
   nov_item = maze_novelty_map(o);
   rendered=true;
  }

  bool isvalid() { 
   return true; 
  }

  void clear() { return; }

  float get_x() { 
    return nov_item->data[0][0];
  }
  float get_y() {
    return nov_item->data[0][1];
  }
  bool solution() {
    return nov_item->solution;
  } 

  ~mazenav() {
  if(g) {
   if(o) delete o;
   else delete g;
  }
  if(nov_item)
	delete nov_item;
  } 
};


class feature_detector {
public:
static float scale(float x,float min,float max) {
 return (x-min)/(max-min);
}
static float scalex(float x,mazenav* mn) {
 return scale(x,mn->nov_item->minx,mn->nov_item->maxx);
}
static float scaley(float x,mazenav* mn) {
 return scale(x,mn->nov_item->miny,mn->nov_item->maxy);
}

static float endx(mazenav* mn) { return scalex(mn->nov_item->end_x,mn); }
static float endy(mazenav* mn) { return scaley(mn->nov_item->end_y,mn); }
static float midx(mazenav* mn) { return scalex(mn->nov_item->mid_x,mn); }
static float midy(mazenav* mn) { return scaley(mn->nov_item->mid_y,mn); }

static float end_goal(mazenav* mn) {
 return mn->nov_item->end_goal_dist / mn->nov_item->max_dist;
}

static float start_dist(mazenav* mn) {
 return mn->nov_item->end_start_dist / mn->nov_item->max_dist;
}

static float closest_goal(mazenav* mn) {
 return mn->nov_item->closest_goal_dist / mn->nov_item->max_dist;
}

static float spd(mazenav* mn) { float s= mn->nov_item->tot_dist/mn->nov_item->timesteps/1.0; 
if(s>1.0) return 1.0;
return s;
}

static float turn(mazenav* mn) { float t= mn->nov_item->tot_turn/mn->nov_item->timesteps/1.0; 
if(t>1.0) return 1.0;
return t;
}

static float coll(mazenav* mn) {

float c= ((float)mn->nov_item->collisions) / 40.0 + 0.5;
if(mn->nov_item->collisions==0)
 c=0.0;

if(c>1.0) return 1.0;
return c;
}

};
