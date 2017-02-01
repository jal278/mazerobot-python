#include <stdint.h>
#include <bzlib.h>
#include <cstdio>
#include <cstdlib>
#include <math.h>
#include <iostream>
#include <fstream>
#include <gsl/gsl_statistics.h>
#include <gsl/gsl_rng.h> 
#include <gsl/gsl_randist.h> 
#include <time.h>

gsl_rng* rng;

using namespace std;

#define CONN_BITS 16
#define STRENGTHS 3
#define MAX_NEIGH CONN_BITS*STRENGTHS
#define MAX_NICHES 300000

double probs[MAX_NEIGH];

void init_probs() {
 for(int i=0;i<MAX_NEIGH;i++)
	probs[i]=1.0/((double)MAX_NEIGH);
}

uint32_t neighborlist[MAX_NEIGH];
int genelist[CONN_BITS];
uint32_t size;

typedef struct {
 uint16_t x;
 uint16_t y;
 uint16_t evolvability;
 uint16_t behaviorhash;   
} behavior;

behavior* data;

typedef struct {
 uint32_t psize;
 uint32_t o_psize;
} node;

typedef struct {
node* graph;
uint32_t* visited_nodes;
uint32_t visited_node_count;

uint16_t* visited_niches;
uint16_t visited_niche_count;

uint64_t* niche_evolvability_tot;
uint64_t* niche_evolvability_cnt;

uint64_t pop_count;
double evolvability_avg;
double evolvability_sampled;
ofstream* anim;
int gen;
} sim;

void calc_neighbors(uint32_t node);
void init_graph(node* graph);
void sim_visit_node(sim* s, uint32_t node, uint32_t amount);
void sim_iteration_complete(sim *s);

void init_sim(sim* s) {
 s->gen=0;
 s->pop_count=0;
 s->anim=NULL;
 s->graph = (node*)malloc(size*sizeof(node));
 init_graph(s->graph);

 s->visited_nodes = (uint32_t*)malloc(size*sizeof(uint32_t));
 s->visited_node_count=0;

 s->visited_niches = (uint16_t*)malloc(MAX_NICHES*sizeof(uint16_t));
 s->visited_niche_count=0;

 s->niche_evolvability_tot = (uint64_t*)malloc(MAX_NICHES*sizeof(uint64_t));
 s->niche_evolvability_cnt = (uint64_t*)malloc(MAX_NICHES*sizeof(uint64_t));

 for(int i=0;i<MAX_NICHES;i++) {
  s->niche_evolvability_tot[i]=0;
  s->niche_evolvability_cnt[i]=0;
 }
 init_probs();
 //initialize population with one individual
 uint32_t i = gsl_rng_uniform_int(rng,size);
 sim_visit_node(s,i,1); //todo_randomzie initial seed
 sim_iteration_complete(s);
}

void sim_visit_node(sim* s, uint32_t n, uint32_t amount) {
 int niche = data[n].behaviorhash;
 int evol = data[n].evolvability;

 if(s->niche_evolvability_cnt[niche]==0) {
  s->visited_niches[s->visited_niche_count]=niche;
  s->visited_niche_count++;
 }

 s->niche_evolvability_cnt[niche]+=amount;
 s->niche_evolvability_tot[niche]+=amount*evol;

 if(s->graph[n].psize==0) {
  s->visited_nodes[s->visited_node_count]=n;
  s->visited_node_count++;
 }
 s->graph[n].psize+=amount;
}

void sim_iteration(sim *s) {
 unsigned int offspring[MAX_NEIGH];

 uint32_t vnc = s->visited_node_count;
 for(uint32_t i=0;i<vnc;i++) {
  uint32_t ind = s->visited_nodes[i];
  uint32_t sz = s->graph[ind].o_psize;
  //now model reproduction over the 48 possibilities
  calc_neighbors(ind);
  gsl_ran_multinomial(rng,MAX_NEIGH,sz,probs,offspring);

  for(int j=0;j<MAX_NEIGH;j++) {
	if(offspring[j]>0)
	 sim_visit_node(s,neighborlist[j],offspring[j]);
  }
 }
 sim_iteration_complete(s);
 s->gen++;
}

void sim_iteration_complete(sim *s) {
 s->pop_count=0;
 s->evolvability_avg=0.0;
 s->evolvability_sampled=0.0;

 for(int i=0;i<s->visited_niche_count;i++) {
  int niche = s->visited_niches[i];
  s->evolvability_sampled+= ((double)s->niche_evolvability_tot[niche])/((double)s->niche_evolvability_cnt[niche]);
  if(s->anim!=NULL) {
   (*s->anim) << s->gen << " " << niche << " " << ((double)s->niche_evolvability_tot[niche])/((double)s->niche_evolvability_cnt[niche]) <<endl;
  }
 }
 s->evolvability_sampled/=s->visited_niche_count;

 double evolv_count=0.0;
 double evolv_tot=0.0;

 for(int i=0;i<s->visited_node_count;i++) {
  uint32_t ind = s->visited_nodes[i];
  s->graph[ind].o_psize = s->graph[ind].psize;
  s->pop_count+= s->graph[ind].psize;

  int evolv = data[ind].evolvability;
  evolv_count+= s->graph[ind].psize;
  evolv_tot+=evolv*s->graph[ind].psize;
 }
 s->evolvability_avg=evolv_tot/evolv_count;
}

void init_graph(node* graph) {
 for(uint32_t i=0;i<size;i++) {
  graph[i].psize=0;
  graph[i].o_psize=0;
 }
}

inline void decode_index(uint32_t node) {
 for(int i=0;i<CONN_BITS;i++)
 {
	genelist[i]=node%3;
	node/=3;
 }
}

inline uint32_t encode_index() {
 uint32_t accum=0;
 for(int i=CONN_BITS-1;i>=0;i--)
 {
	accum*=3;
	accum+=genelist[i];
 }
 return accum;
}

void calc_neighbors(uint32_t node) {
 int cnt=0;
 decode_index(node);
 for(int i=0;i<CONN_BITS;i++) {
  int saved_bit=genelist[i];
  for(int j=0;j<3;j++) {
    genelist[i]=j;
    neighborlist[cnt]=encode_index();
    cnt++;
  }
  genelist[i]=saved_bit;
 }
 //cout << cnt << endl;
}


int main(int argc, char** x) {
 char fname[100];
 sprintf(fname,"%s.dat",x[1]);
 ofstream log(fname);
 sprintf(fname,"%s.anim",x[1]); 
 ofstream anim(fname);
 size=pow(3,16);
 long int behavior_byte_size=size*8;
 
 rng =gsl_rng_alloc(gsl_rng_taus);
 gsl_rng_set(rng,time(NULL));
 
 data = (behavior*)malloc(behavior_byte_size);

 int error;
 FILE* f = fopen("storage.dat.bz2","rb");
 BZFILE *bz2= BZ2_bzReadOpen(&error,f,1,0,NULL,0);
 BZ2_bzRead(&error,bz2,(void*)data,behavior_byte_size); 

//#define SIM
#ifdef SIM 
 sim s;
 init_sim(&s);
 s.anim= &anim;
 for(int i=0;i<30;i++) {
  log << i << " " << s.pop_count << " " << s.visited_node_count << " " << s.visited_niche_count << " " << s.evolvability_avg << " " << s.evolvability_sampled << endl;
  cout << "gen " << i << endl;
  cout << "pop size:" << s.pop_count << endl;
  cout << "unique genomes:" << s.visited_node_count << endl;
  cout << "niches explored:" << s.visited_niche_count << endl;
  cout << "true evolvability avg:" << s.evolvability_avg << endl;
  cout << "niche evolvability avg:" << s.evolvability_sampled << endl;
  sim_iteration(&s); 
 }
#endif

//evolvability correlation calculations
#define STATS true
if(STATS) {
double* ev_orig = (double*)malloc(size*sizeof(double));
double* ev_off = (double*)malloc(size*sizeof(double));
//int length=size;
int length=100000;
// for(int i=0;i<size;i++) {
 for(int sample=0;sample<length;sample++) {
   int i = gsl_rng_uniform_int(rng,size);
 
  //if(i%100000==0)
  // cout << i << endl;

  /*
  calc_neighbors(i);
  int evolvability=0;
  for(int j=0;j<16*3;j++) 
   evolvability+=data[neighborlist[j]].evolvability;

  double ev_avg = ((double)evolvability)/48.0;
  ev_off[sample]=ev_avg;
  */
  ev_orig[sample]=(double)data[i].evolvability;
  double dx = data[i].x - 31.0;
  double dy = data[i].y - 20.0;
  dx*=dx; dy*=dy;
  double fitness = sqrt(dx+dy);
//#define PRINTDATA 
#ifdef PRINTDATA
   cout << data[i].x << " " << data[i].y << " " << data[i].evolvability << " " << fitness << endl;
#endif
 }

 //#define PRINTSTATS
 #ifdef PRINTSTATS
// cout <<"correlation" << gsl_stats_correlation(ev_orig,1,ev_off,1,length) << endl;

 cout <<"max" << gsl_stats_max(ev_orig,1,length) << endl;
 cout <<"min" << gsl_stats_min(ev_orig,1,length) << endl;
 cout <<"mean" << gsl_stats_mean(ev_orig,1,length) << endl;
 #endif
 free(ev_orig);
 free(ev_off);
}









 free(data);
 return 0;
}

