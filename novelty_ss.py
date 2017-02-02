import pdb
import numpy as np
from PIL import Image, ImageDraw
from scipy.spatial import cKDTree as kd
import mazepy
import precomputed_domain
import entropy

novelty=False
disp=False
SZX=SZY=400
NS_K = 10
ELITE = 3
screen = None
archive=[]
if novelty:
 tourn_size = 2
else:
 tourn_size = 3

from entropy import *
domain = default_domain
precomputed = True
if precomputed:
 domain = precomputed_domain.precomputed_domain_interface("medium")
 entropy.default_domain = domain 

if disp:
 import pygame
 from pygame.locals import *
 pygame.init()
 pygame.display.set_caption('Viz')
 screen =pygame.display.set_mode((SZX,SZY))
 
 background = pygame.Surface(screen.get_size())
 background = background.convert()
 background.fill((250, 250, 250,255))

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
  x,y = domain.get_behavior(robot)
  x=x*SZX
  y=y*SZY
  rect=(int(x),int(y),5,5)
  pygame.draw.rect(screen,(255,0,0),rect,0)

 if novelty:
  for robot in archive:
   x,y = domain.get_behavior(robot)
   x=x*SZX
   y=y*SZY
   rect=(int(x),int(y),5,5)
   pygame.draw.rect(screen,(0,255,0),rect,0)

 pygame.display.flip()


def eval_pop(population):
  #pdb.set_trace()
  data=numpy.vstack([k.behavior for k in population+archive])
  tree=kd(data)  
  for art in population:
   eval_ind(art,tree)
  return tree 

def eval_ind(art,tree):
 if novelty:
  nearest,indexes=tree.query(art.behavior,NS_K)
  art.raw_fitness=domain.get_fitness(art)
  art.fitness=nearest.sum()
 else:
  art.fitness=domain.get_fitness(art)
  art.raw_fitness = art.fitness
 
def read_maze(fname='hard_maze.txt'):
 lines = open(fname).read().split("\n")[7:-1]
 coords = [[float(x) for x in line.split()] for line in lines]
 return coords

def transform_dim(c,rng_o,rng_n):
 interval = (c-rng_o[0])/(rng_o[1]-rng_o[0])
 return rng_n[0] + (rng_n[1]-rng_n[0])*interval

def transform_size(c,rng_o,rng_n):
 size_old = rng_o[1]-rng_o[0]
 size_new = rng_n[1]-rng_n[0]
 return (c/size_old)*size_new

def transform_pnt(c,xrng_o,yrng_o,xrng_n,yrng_n):
 return [transform_dim(c[0],xrng_o,xrng_n),transform_dim(c[1],yrng_o,yrng_n)]

def transform_line(line,xrng_old,yrng_old,xrng_new,yrng_new):
 return transform_pnt(line[0:2],xrng_old,yrng_old,xrng_new,yrng_new)+transform_pnt(line[2:],xrng_old,yrng_old,xrng_new,yrng_new)

def draw_maze(walls,agent,sz=64,fname=None):
 maze = Image.new('RGB',(sz,sz),(255,255,255))

 wallx = [c[0] for c in walls] + [c[2] for c in walls]
 wally = [c[1] for c in walls] + [c[3] for c in walls]

 buf = 5
 xrng = (min(wallx)-buf,max(wallx)+buf)
 yrng = (min(wally)-buf,max(wally)+buf) 
 
 d = ImageDraw.Draw(maze)
 for line in walls: 
  x0,y0,x1,y1 = transform_line(line,xrng,yrng,(0,sz-1),(0,sz-1))
  d.line([x0,y0,x1,y1],fill=(0,0,0),width=2)

 hx,hy,heading = agent
 xprime,yprime = transform_pnt((hx,hy),xrng,yrng,(0,sz-1),(0,sz-1))
 radiusx = transform_size(8.0,xrng,(0,sz-1))
 radiusy = transform_size(8.0,yrng,(0,sz-1))
 heading_rad = (heading+180)/180.0 * 3.14

 xprime_head = xprime+math.cos(heading_rad)*radiusx
 yprime_head = yprime+math.sin(heading_rad)*radiusy

 d.ellipse([xprime-radiusx,yprime-radiusy,xprime+radiusx,yprime+radiusy],(255,0,0),(255,0,0))
 
 draw_heading=False
 if draw_heading:
  d.line([xprime,yprime,xprime_head,yprime_head],fill=(0,128,0),width=2)

 if False:
  from pylab import *
  imshow(maze)
  show()

 if fname!=None:
  maze.save(fname) 

 return numpy.array(maze)

def do_search(psize,maxevals):

if(__name__=='__main__'):
 evo_fnc = calc_evolvability_entropy
 #initialize maze stuff with "medium maze" 
 #mazepy.mazenav.initmaze("medium_maze_list.txt","neat.ne")
 mazepy.mazenav.initmaze("hard_maze_list.txt","neat.ne")
 maze_desc = read_maze('hard_maze.txt')
 #mazepy.mazenav.initmaze("medium_maze_list.txt")
 mazepy.mazenav.random_seed()

 robot=None

 behavior_density=defaultdict(int)
 population=[]
 psize=500

 for k in range(psize):
  robot=domain.generator()
  robot.init_rand()
  robot.mutate()
  robot.map()
  robot.parent=None
  behavior_density[map_into_grid(robot,domain)]+=1
  population.append(robot)

 tree=None
 tree=eval_pop(population)
 solved=False

 evals=psize

 max_evals=500*500 #1000000

 while evals < max_evals and not solved:
  #population.sort(key=lambda x:x.fitness,reverse=True)
  if(evals%1000==0):
   keys=behavior_density.keys()
   print evals,len(keys),calc_population_entropy(population),max([x.raw_fitness for x in population])
   if(disp):
    render(population,behavior_density)
 
  parents=random.sample(population,tourn_size)
  parent=reduce(lambda x,y:x if x.fitness>y.fitness else y,parents)

  child=parent.copy()
  child.mutate()
  child.parent=parent
  child.map()

  if False:
   x=mazepy.feature_detector.endx(child)
   y=mazepy.feature_detector.endy(child)
   print child.get_x()
   print child.get_y()
   print child.get_heading()
   img=draw_maze(maze_desc,(child.get_x(),child.get_y(),child.get_heading()),fname='imgs/%d-%d.png'%(child.get_x(),child.get_y()))

  population.append(child)
  behavior_density[map_into_grid(child,domain)]+=1

  if(evals%50!=0):
   eval_ind(child,tree) 
  else:
   if novelty:
    eval_pop(population)
   else:
    eval_ind(child,tree) 
  
  if(child.solution()):
    solved=True
 
  if(random.random()<0.01):
   archive.append(child)

  to_kill_idx=np.random.randint(0,len(population),3)
  to_kill_idx=reduce(lambda x,y:x if population[x].fitness<population[y].fitness else y,to_kill_idx)
  to_kill=population[to_kill_idx]
  population=population[:to_kill_idx]+population[to_kill_idx+1:]

  del to_kill
  evals+=1


 #run genome in the maze simulator

 #calculate evolvability
 print child.solution()
 asfd
 print "evolvability:", evo_fnc(child,1000)

 """
 robot=mazepy.mazenav()
 robot.init_rand()
 robot.mutate()
 robot.map()
 print "evolvability:", evo_fnc(robot,1000)
 """

 optimize_evolvability(child)
