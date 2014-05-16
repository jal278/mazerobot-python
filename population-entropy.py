disp=True
SZX=SZY=400
screen = None

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
 pygame.display.flip()

from entropy import *
if(__name__=='__main__'):
 evo_fnc = calc_evolvability_entropy
 #initialize maze stuff with "medium maze" 
 mazepy.mazenav.initmaze("hard_maze_list.txt")
 #mazepy.mazenav.initmaze("medium_maze_list.txt")
 mazepy.mazenav.random_seed()

 robot=None

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
 child=None
 max_evals=1000000
 while evals < max_evals: #not solved:
  keys=population.keys()

  evals+=1
  if(evals%1000==0):
   print evals,len(keys),calc_population_entropy(whole_population)
   if(disp):
    render(whole_population)
  pniche=random.choice(keys)
  parent=random.choice(population[pniche])

  child=parent.copy()
  child.mutate()
  child.map()

  if(child.solution()):
   solved=True

  population[map_into_grid(child)].append(child)
  whole_population.append(child)

  niche=most_populus(population)

  to_kill=random.choice(population[niche])

  population[niche].remove(to_kill)
  whole_population.remove(to_kill)
  del to_kill
  if(len(population[niche])==0):
   population.pop(niche)

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
