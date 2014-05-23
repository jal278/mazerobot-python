import sys
import random

calc_evo=True
extinction=True
seed=-1
outfile="out"
if(len(sys.argv)>1):
 extinction = sys.argv[1]=='e'
 seed = int(sys.argv[2])
 outname= sys.argv[3]

disp=False
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
evo_fnc = calc_evolvability_cnt

def killbot(to_kill,niche,population,whole_population):
  population[niche].remove(to_kill)
  whole_population.remove(to_kill)
  del to_kill
  if(len(population[niche])==0):
   population.pop(niche)



if(__name__=='__main__'):
 log_file=open(outfile+".log","w")
 evo_file=open(outfile+".evo","w")
 #evo_fnc = calc_evolvability_entropy
 #initialize maze stuff with "medium maze" 

 mazepy.mazenav.initmaze("hard_maze_list.txt")
 #mazepy.mazenav.initmaze("medium_maze_list.txt")
 if(seed==-1):
  mazepy.mazenav.random_seed()
 else:
  random.seed(seed)
  mazepy.mazenav.seed(seed)


 robot=None

 population=defaultdict(list)
 whole_population=[]
 psize=2000
 repop=0

 for k in range(psize):
  robot=mazepy.mazenav()
  robot.init_rand()
  robot.mutate()
  robot.map()
  population[map_into_grid(robot)].append(robot)
  whole_population.append(robot)
 solved=False

 evals=0 #psize
 child=None
 max_evals=2000000

 while evals < max_evals: #not solved:
  keys=population.keys()

  if(evals%1000==0):
   quant=evals,len(keys),calc_population_entropy(whole_population),complexity(whole_population)
   print quant
   log_file.write(str(quant)+"\n")

   if(disp):
    render(whole_population)
   sys.stdout.flush()
  pniche=random.choice(keys)
  parent=random.choice(population[pniche])

  child=parent.copy()
  child.mutate()
  child.map()

  if(child.solution()):
   solved=True

  population[map_into_grid(child)].append(child)
  whole_population.append(child)
  if(repop==0):
   niche=most_populus(population)
   to_kill=random.choice(population[niche])
   killbot(to_kill,niche,population,whole_population)
  else:
   repop-=1

  if extinction and evals>30000 and (evals+1)%(10000)==0:
   xc=random.randint(0,grid_sz)
   yc=random.randint(0,grid_sz)
   rad=grid_sz*0.45
   niches_to_kill=[]

   for x in range(grid_sz):
    for y in range(grid_sz):
     dx=abs(x-xc)
     dy=abs(y-yc)
     #if min(dx,grid_sz-dx)**2+min(dy,grid_sz-dy)**2 < rad**2:
     niches_to_kill.append((x,y))

   survivors=random.sample(population.keys(),10)
   for k in survivors:
     niches_to_kill.remove(k)

   repop=0
   for niche in niches_to_kill:
    orgs=population[niche][:]
    repop+=len(orgs)
    for x in orgs:
     killbot(x,niche,population,whole_population)
    if niche in population:
     population.pop(niche)   
  if(calc_evo and evals%250000==0):
   #run genome in the maze simulator
   print "EVO-CALC"
   for org in random.sample(whole_population,200): 
    evo=evo_fnc(org,1000)
    print "evolvability:", evo
    evo_file.write(str(evals)+" "+str(evo)+"\n")
   print "EVO-CALC END"
  evals+=1

 """
 robot=mazepy.mazenav()
 robot.init_rand()
 robot.mutate()
 robot.map()
 print "evolvability:", evo_fnc(robot,1000)
 
 optimize_evolvability(child)
 """
