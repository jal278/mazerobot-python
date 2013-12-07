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

 robot.map()
 x1=mazepy.feature_detector.endx(robot)

 for x in range(mutations):
  mutant=robot.copy()
  mutant.mutate()
  mutant.map()
  #if(mutant.solution()): 
  # print "solved"
  key=map_into_grid(mutant)
  grids[key]+=1

 robot.map()
 x2=mazepy.feature_detector.endx(robot)
 #print x1,x2

 return grids

def calc_population_entropy(pop):
 return distr_entropy(population_to_grids(pop),len(pop))
 
def calc_evolvability_entropy(robot,mutations):
 return distr_entropy(mutations_to_grids(robot,mutations),mutations)

def calc_evolvability_cnt(robot,mutations):
 return len(mutations_to_grids(robot,mutations).keys())



def optimize_evolvability(robot=None):
 evo_fnc = calc_evolvability_entropy
 #initialize maze stuff with "medium maze" 


 population=defaultdict(list)
 whole_population=[]
 psize=10
 e_samp=400
 if(robot==None):
  for k in range(psize):
   robot=mazepy.mazenav()
   robot.init_rand()
   robot.mutate()
   robot.map()
   robot.fitness=evo_fnc(robot,e_samp)
   whole_population.append(robot)
 else:
   for k in range(psize):
    robot2=robot.copy()
    robot2.map()
    robot2.fitness=evo_fnc(robot,e_samp)
    whole_population.append(robot2)

 solved=False

 evals=psize
 child=None
 while not solved:
  evals+=1

  parent=random.choice(whole_population)
  parent.fitness=evo_fnc(parent,e_samp)
  child=parent.copy()
  child.mutate()
  child.map()
  child.fitness=evo_fnc(child,e_samp)

  if(child.solution()):
   #solved=True
   pass
  whole_population.append(child)
  whole_population.sort(key=lambda k:k.fitness,reverse=True)

  to_kill=whole_population[-1]
  #print to_kill.fitness
  whole_population.remove(to_kill)
  del to_kill

  if(evals%1==0):
   print evals,calc_population_entropy(whole_population),whole_population[0].fitness,whole_population[-1].fitness
 #run genome in the maze simulator

 #calculate evolvability
 print child.solution()
 print "evolvability:", evo_fnc(child,1000)

 robot=mazepy.mazenav()
 robot.init_rand()
 robot.mutate()
 robot.map()
 print "evolvability:", evo_fnc(robot,1000)
