import math
import mazepy
import random
from collections import defaultdict
grid_sz=30

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

evo_fnc = calc_evolvability_entropy

if(__name__=='__main__'):
 #initialize maze stuff with "medium maze" 
 mazepy.mazenav.initmaze("hard_maze_list.txt")
 mazepy.mazenav.random_seed()

 population=defaultdict(list)
 whole_population=[]
 psize=1500

 for k in range(psize):
  robot=mazepy.mazenav()
  robot.init_rand()
  robot.mutate()
  robot.map()
  population[map_into_grid(robot)].append(robot)
  whole_population.append(robot)
 solved=False

 evals=psize
 while not solved:
  evals+=1
  if(evals%1000==0):
   print calc_population_entropy(whole_population)

  keys=population.keys()
  pniche=random.choice(keys)
  parent=random.choice(population[pniche])
  child=parent.copy()
  child.mutate()
  child.map()

  if(child.solution()):
   solved=True

  population[map_into_grid(robot)].append(child)
  whole_population.append(child)

  to_comp = random.sample(keys,2)    
  larger=to_comp[0]
  if(len(population[to_comp[1]])>len(population[to_comp[0]])):
   larger=to_comp[1]
  to_kill=random.choice(population[larger])

  population[larger].remove(to_kill)
  whole_population.remove(to_kill)
  del to_kill
  if(len(population[larger])==0):
   population.pop(larger)

 #run genome in the maze simulator

 #calculate evolvability
 print "evolvability:", evo_fnc(robot,400)
 print "evolvability:", evo_fnc(robot,400)
 print "evolvability:", evo_fnc(robot,400)
