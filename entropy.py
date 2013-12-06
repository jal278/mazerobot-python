import math
import mazepy
import random
from collections import defaultdict
grid_sz=20

#a function to map a robot's behavior into a grid of niches
def map_into_grid(robot):
 x=mazepy.feature_detector.endx(robot)
 y=mazepy.feature_detector.endy(robot)
 x_grid=int(x*(grid_sz-1))
 y_grid=int(y*(grid_sz-1))
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

def most_populus(pop):
 mx_s=0
 best=None
 for k in pop:
  if len(pop[k])>mx_s:
   best=k
   mx_s=len(pop[k])
 return best

def population_to_grids(pop):
 grids=defaultdict(float)
 for k in pop:
  key=map_into_grid(k)
  grids[key]+=1
 return grids 

def mutations_to_grids(robot,mutations):
 grids=defaultdict(float)
 for x in range(mutations):
  mutant=robot.copy()
  mutant.mutate()
  mutant.map()
  key=map_into_grid(mutant)
  grids[key]+=1
 return grids

def calc_population_entropy(pop):
 return distr_entropy(population_to_grids(pop),len(pop))
 
def calc_evolvability_entropy(robot,mutations):
 return distr_entropy(mutations_to_grids(robot,mutations),mutations)

def calc_evolvability_cnt(robot,mutations):
 return len(mutations_to_grids(robot,mutations).keys())


