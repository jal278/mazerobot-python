disp=True
SZX=SZY=400
NS_K = 20
ELITE = 5
screen = None

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

def render(pop):
 global screen,background
 screen.blit(background, (0, 0))
 for robot in pop:
  x=mazepy.feature_detector.endx(robot)*SZX
  y=mazepy.feature_detector.endy(robot)*SZY
  rect=(int(x),int(y),5,5)
  pygame.draw.rect(screen,(255,0,0),rect,0)
 for robot in archive:
  x=mazepy.feature_detector.endx(robot)*SZX
  y=mazepy.feature_detector.endy(robot)*SZY
  rect=(int(x),int(y),5,5)
  pygame.draw.rect(screen,(0,255,0),rect,0)
 pygame.display.flip()

from entropy import *
if(__name__=='__main__'):
 evo_fnc = calc_evolvability_entropy
 #initialize maze stuff with "medium maze" 
 mazepy.mazenav.initmaze("hard_maze_list.txt","neat.ne")
 #mazepy.mazenav.initmaze("medium_maze_list.txt")
 mazepy.mazenav.random_seed()

 robot=None

 behavior_density=defaultdict(int)
 population=[]
 psize=250

 for k in range(psize):
  robot=mazepy.mazenav()
  robot.init_rand()
  robot.mutate()
  robot.map()
  behavior_density[map_into_grid(robot)]+=1
  population.append(robot)

 solved=False

 evals=psize

 max_evals=1000000
 archive=[]

 while evals < max_evals: #not solved:
  
  for art in population:
   art.dists=[((art.behavior-x.behavior)**2).sum() for x in population]
   arch_dists=[((art.behavior-x.behavior)**2).sum() for x in archive]
   art.dists+=arch_dists
   art.dists.sort()
   art.fitness = sum(art.dists[:NS_K])
   art.raw_fitness = art.fitness
 
  population.sort(key=lambda x:x.fitness,reverse=True)
  new_population=[]
  child=None
  for x in xrange(psize):
   if x<ELITE:
    child=population[x].copy()
   else: 
    parents=random.sample(population,2)
    parent=reduce(lambda x,y:x if x.fitness>y.fitness else y,parents)
    child=parent.copy()
    child.mutate()

   child.map() 
   behavior_density[map_into_grid(child)]+=1

   new_population.append(child)
   if(child.solution()):
    solved=True
  archive.append(random.choice(population))
  evals+=psize
  keys=behavior_density.keys()
  print evals,len(keys),calc_population_entropy(population)
  if(disp):
   render(population)

  population=new_population


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
