import math
import mazepy
from collections import defaultdict
grid_sz=20

#a function to map a robot's behavior into a grid of niches
def map_into_grid(robot):
 x=mazepy.feature_detector.endx(robot)
 y=mazepy.feature_detector.endy(robot)
 x_grid=int(x*(grid_sz-1))
 y_grid=int(x*(grid_sz-1))
 return (x_grid,y_grid)

def distr_entropy(grids,samples):
 total_grids=grid_sz*grid_sz
 keys=grids.keys()
 entr=0.0
 fsamp=float(samples)
 for key in keys:
  p=grids[key]/fsamp
  entr+=p*math.log(p)
 return -entr

def mutations_to_grids(robot,mutations):
 grids=defaultdict(float)
 for x in range(mutations):
  mutant=robot.copy()
  mutant.mutate()
  mutant.map()
  key=map_into_grid(mutant)
  grids[key]+=1
 return grids

def calc_evolvability_entropy(robot,mutations):
 return distr_entropy(mutations_to_grids(robot,mutations),mutations)

def calc_evolvability_cnt(robot,mutations):
 return len(mutations_to_grids(robot,mutations).keys())

evo_fnc = calc_evolvability_entropy
if(__name__=='__main__'):
 #initialize maze stuff with "medium maze" 
 mazepy.mazenav.initmaze("hard_maze_list.txt")
 mazepy.mazenav.random_seed()

 #create initial genome
 robot=mazepy.mazenav()


 #initalize it randomly and mutate it once for good measure
 robot.init_rand()
 robot.mutate()

 #run genome in the maze simulator
 robot.map()

 #calculate evolvability
 print "evolvability:", evo_fnc(robot,400)
 print "evolvability:", evo_fnc(robot,400)
 print "evolvability:", evo_fnc(robot,400)
