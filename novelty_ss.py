from scipy.spatial import cKDTree as kd
disp=True
SZX=SZY=400
NS_K = 20
ELITE = 3
screen = None
archive=[]

def fitness(robot):
 return -mazepy.feature_detector.end_goal(robot)

if disp:
 import pygame
 from pygame.locals import *
 pygame.init()
 pygame.display.set_caption('Viz')
 screen =pygame.display.set_mode((SZX,SZY))
 
 background = pygame.Surface(screen.get_size())
 background = background.convert()
 background.fill((250, 250, 250))

def render(pop,bd=None):
 global screen,background
 screen.blit(background, (0, 0))

 if (bd!=None):
  for key in bd:
   x,y=float(key[0])/(grid_sz-1)*SZX,float(key[1])/(grid_sz-1)*SZY
   x1,y1=int(1.0/(grid_sz-1)*SZX)+1,int(1.0/(grid_sz-1)*SZY)+1
   rect=(int(x),int(y),x1,y1)
   col=int(255*min(bd[key],100)/100.0)
   pygame.draw.rect(screen,(0,0,col),rect,0)

 for robot in pop:
  x=mazepy.feature_detector.endx(robot)*SZX
  y=mazepy.feature_detector.endy(robot)*SZY
  rect=(int(x),int(y),5,5)
  pygame.draw.rect(screen,(255,0,0),rect,0)
 pygame.display.flip()

from entropy import *

def eval_pop(population):
  data=numpy.vstack([k.behavior for k in population+archive])
  tree=kd(data)  
  for art in population:
   eval_ind_k(art,tree)
  return tree 

def eval_ind(art,population,tree):
   eval_ind_k(art,tree)
   return
   art.dists=[((art.behavior-x.behavior)**2).sum() for x in population]
   arch_dists=[((art.behavior-x.behavior)**2).sum() for x in archive]
   art.dists+=arch_dists
   art.dists.sort()
   #art.raw_fitness = art.fitness
   art.fitness = sum(art.dists[:NS_K])

def eval_ind_k(art,tree):
 nearest,indexes=tree.query(art.behavior,NS_K)
 art.fitness=sum(nearest)

if(__name__=='__main__'):
 evo_fnc = calc_evolvability_entropy
 #initialize maze stuff with "medium maze" 
 mazepy.mazenav.initmaze("hard_maze_list.txt")
 #mazepy.mazenav.initmaze("medium_maze_list.txt")
 mazepy.mazenav.random_seed()

 robot=None

 behavior_density=defaultdict(int)
 population=[]
 psize=1000

 for k in range(psize):
  robot=mazepy.mazenav()
  robot.init_rand()
  robot.mutate()
  robot.map()
  robot.parent=None
  behavior_density[map_into_grid(robot)]+=1
  population.append(robot)

 tree=eval_pop(population)
 solved=False

 evals=psize

 max_evals=1000000

 while evals < max_evals: #not solved:
  #population.sort(key=lambda x:x.fitness,reverse=True)
  evals+=1
  if(evals%1000==0):
   keys=behavior_density.keys()
   print evals,len(keys),calc_population_entropy(population)
   if(disp):
    render(population,behavior_density)
 
  parents=random.sample(population,3)
  parent=reduce(lambda x,y:x if x.fitness>y.fitness else y,parents)
  child=parent.copy()
  child.mutate()
  child.parent=parent
  child.map()

  population.append(child)
  behavior_density[map_into_grid(child)]+=1

  if(evals%25!=0):
   eval_ind(child,population,tree) 
  else:
   eval_pop(population)

  if(child.solution()):
    solved=True
  if(random.random()<0.01):
   archive.append(child)

  to_kill=random.sample(population,3)
  to_kill=reduce(lambda x,y:x if x.fitness<y.fitness else y,parents)
  population.remove(to_kill)
  del to_kill


 #run genome in the maze simulator

 #calculate evolvability
 print child.solution()
 print "evolvability:", evo_fnc(child,1000)

 robot=mazepy.mazenav()
 robot.init_rand()
 robot.mutate()
 robot.map()
 print "evolvability:", evo_fnc(robot,1000)
 
 optimize_evolvability(child)
