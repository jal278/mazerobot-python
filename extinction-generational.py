import sys
import random
import operator

test=True

calc_evo=True
extinction=True
seed=-1
outfile="out"
nefile="neat.ne"


#was 40000
interval=40000
niche_capacity=10

if(len(sys.argv)>1):
 extinction = sys.argv[1]=='e'
 seed = int(sys.argv[2])
 outfile= sys.argv[3]
 nefile=sys.argv[4]
 if(len(sys.argv)>5):
  interval=int(sys.argv[5])

disp=False
SZX=SZY=400
screen = None

if test:
 calc_evo=False
 disp=True

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

 mazepy.mazenav.initmaze("hard_maze_list.txt",nefile)
 #mazepy.mazenav.initmaze("medium_maze_list.txt")
 if(seed==-1):
  mazepy.mazenav.random_seed()
 else:
  random.seed(seed)
  mazepy.mazenav.seed(seed)

 eflag=False
 robot=None

 population=defaultdict(list)
 whole_population=[]
 psize=1
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
 max_evals=2500 #3000001

 best_fit=-1000000.0
 best_fit_org=None
 best_evo=0
 best_evo_org=None
 gen=0
 while gen < max_evals: #not solved:
  keys=population.keys()

  if(disp and eflag):
   render(whole_population)
   eflag=False
  if(gen%1==0):
   quant=evals,len(keys),calc_population_entropy(whole_population),complexity(whole_population),best_fit,gen
   print quant
   log_file.write(str(quant)+"\n")

   if(disp):
    render(whole_population)
   sys.stdout.flush()
 
  new_population=defaultdict(list)
  new_whole_pop=[]

  for pniche in keys:
   for parent in population[pniche]:
    for offspring in range(2):
     #pniche=random.choice(keys)
     #parent=random.choice(population[pniche])
     child=parent.copy()
     child.mutate()
     child.map()
     evals+=1

     if(fitness(child)>best_fit):
      best_fit=fitness(child)
      best_fit_org=child.copy()
     if(child.solution()):
      solved=True

     off_niche = map_into_grid(child)
     if(len(new_population[off_niche])<niche_capacity):
      new_population[off_niche].append(child)
      new_whole_pop.append(child)

  for k in whole_population:
   del k


  if extinction and gen>10 and (gen-1)%(interval)==0:
   eflag=True
   niches_to_kill=[]
   for x in range(grid_sz):
    for y in range(grid_sz):
     niches_to_kill.append((x,y))
   survivors=new_population.keys()
   try:
    survivors=random.sample(new_population.keys(),10)
   except:
    pass
   survivor_orgs=reduce(operator.add,[new_population[x] for x in survivors])
 
   for niche in niches_to_kill:
    orgs=new_population[niche][:]
    for x in orgs:
      if x not in survivor_orgs:
       killbot(x,niche,new_population,new_whole_pop)
    if niche in new_population and niche not in survivors:
     new_population.pop(niche)
   

  whole_population=new_whole_pop
  population=new_population
  gen+=1

  """ 
  if(repop==0):
   niche=most_populus(population)
   to_kill=random.choice(population[niche])
   killbot(to_kill,niche,population,whole_population)
  else:
   repop-=1

   #for k in survivors:
   #  niches_to_kill.remove(k)

   repop=0
   for niche in niches_to_kill:
    orgs=population[niche][:]
    repop+=len(orgs)
    for x in orgs:
      if x not in survivor_orgs:
       killbot(x,niche,population,whole_population)
    if niche in population and niche not in survivors:
     population.pop(niche)
  """

  if(calc_evo and evals%250000==0):
   #run genome in the maze simulator
   print "EVO-CALC"
   for org in random.sample(whole_population,200): 
    evo=evo_fnc(org,1000)
    if evo>best_evo:
     best_evo=evo
     best_evo_org=org.copy()
    print "evolvability:", evo
    evo_file.write(str(evals)+" "+str(evo)+"\n")
   print "EVO-CALC END"
   evo_file.flush()
 
 best_evo_org.save(outfile+"_bestevo.dat") 
 best_fit_org.save(outfile+"_bestfit.dat") 
 if solved:
  best_fit_org.save(outfile+"_solution.dat")

 """
 robot=mazepy.mazenav()
 robot.init_rand()
 robot.mutate()
 robot.map()
 print "evolvability:", evo_fnc(robot,1000)
 
 optimize_evolvability(child)
 """
