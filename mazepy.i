%include "carrays.i"
%include "std_vector.i"
using namespace std;
namespace std {
%template(vectorf) vector<float>;
}
%array_class(float,floatArray);
%newobject *::copy;
%module mazepy
%{
#include "maze_py.h"
%}

#include "maze_py.h"
class mazewrapper {
public:
  mazewrapper();
  void load_env(const char* ename);
  void reset();
  float goal_dist();
  vector<float> get_state();
  void take_action(int a);
  void set_outputs(float o1, float o2, float o3);
  vector<float> get_walls();
  vector<float> get_behavior();
  ~mazewrapper();
}; 

class feature_detector {
public:
static float end_goal(mazenav* mn);
static float start_dist(mazenav* mn);
static float closest_goal(mazenav* mn);
static float endx(mazenav* mn);
static float endy(mazenav* mn);
static float midx(mazenav* mn);
static float midy(mazenav* mn);
static float spd(mazenav* mn);
static float coll(mazenav* mn);
static float turn(mazenav* mn);
static float state_entropy(mazenav* mn);
};

class mazenav {
public: 
 void make_random();

 static void seed(int sd);
 static void random_seed();
 mazenav();

  mazenav* copy();
  int complexity();

  void map();
  static void initmaze(const char* mazefile,const char* nefile);
  void mutate();
  bool isvalid();
  void clear();
  double distance(mazenav* other);
  void init_rand();
 
  void save(const char *fname);
  void load_new(const char *fname);

  float get_x(); 
  float get_y();
  bool viable();
  bool solution();
  ~mazenav();

};
