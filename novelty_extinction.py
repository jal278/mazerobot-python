import os
import sys
import cPickle as pickle
from scipy.spatial import cKDTree as kd

test=os.path.isfile("visualize")

collision=True
calc_evo=True
extinction=True
seed=-1
outfile="out"
nefile="neat.ne"
disp=False
#was 40000
interval=2000

if test:
 calc_evo=False
 disp=True

best_fit=-1000000.0
best_fit_org=None
best_evo=0
best_evo_org=None

if(len(sys.argv)>1):
 extinction = sys.argv[1]=='e'
 seed = int(sys.argv[2])
 outfile= sys.argv[3]
 nefile=sys.argv[4]
 if(len(sys.argv)>5):
  interval=int(sys.argv[5])


SZX=SZY=400
NS_K = 20
ELITE = 3
screen = None

def fitness_end(robot):
 return -mazepy.feature_detector.end_goal(robot)


def d_score(rset,z):
 pts=numpy.vstack([k.behavior for k in rset])
 zpt=numpy.array(z.behavior)

 sz=len(rset)
 best=100000

 for x in xrange(sz):
    d=((pts[x]-zpt)**2).sum()
    if d<best:
     best=d

 return best
   
def optimize_pick(pop,size):
 print "picking..."
 rset=[]
 rset.append(random.choice(pop))
 while len(rset)<size:
  bscore=-1000
  choices=[]
  for k in pop:
   if k in rset:
    continue
   score=d_score(rset,k)
   choices.append((score,k))
  choices.sort(reverse=True)
  #print choices
  quarter=len(choices)/5
  rset.append(random.choice(choices[:quarter])[1])
 print "done..."
 return rset

def exploration_measure(evolve):
 lrng=0.0
 brng=1.0

 pts=numpy.vstack([k.behavior for k in evolve.population])
 nsamp=5000
 samples=numpy.random.uniform(lrng,brng,(nsamp,pts.shape[1]))
 tot=0.0
 for k in range(samples.shape[0]):
  dists=((pts-samples[k])**2) #.sum(0)
  tot+=dists.sum(1).min()
 return -tot

def exploration_measure1(evolve):
 pts=numpy.vstack([k.behavior for k in evolve.population])
 num=40 #pts.shape[0]
 tot=0.0
 for k in range(pts.shape[0]):
  dists=((pts-pts[k])**2).sum(1)
  dists.sort()
  tot+= dists[:num].sum()
 #tot/=pts.shape[0]
 return tot

class ss_evolve:
 def __init__(self,eval_budget=5000,psize=250,do_fit=False,copy=None): 
  self.do_fitness=do_fit
  self.archive=[]
  self.population=[]
  self.highest_fitness = -10000
  arc=None
  pop=None
  
  if copy!=None:
   arc=copy.archive
   pop=copy.population
   print "copy engaged"

  if arc!=None:
   self.archive=[k.copy(True) for k in arc]
   [map_into_grid(k) for k in self.archive]

  if pop!=None:
   self.population=[k.copy(True) for k in pop]
   [map_into_grid(k) for k in self.population]

  self.behavior_density=defaultdict(int)
  self.psize=psize
  self.solution=None
  self.evals=0

  if copy==None:
   print "regen.."
   for k in range(self.psize):
    robot=mazepy.mazenav(collision)
    robot.init_rand()
    robot.mutate()
    robot.map()
    robot.parent=None
    self.behavior_density[map_into_grid(robot)]+=1
    self.population.append(robot)
   self.evals=self.psize
  self.eval_pop()
  self.solved=False
  self.max_evals=eval_budget
 

 def eval_pop(self):
  if not self.do_fitness:
   data=numpy.vstack([k.behavior for k in self.population+self.archive])
   self.tree=kd(data)

  for art in self.population:
   self.eval_ind_k(art)

 def eval_ind(self,art):
   self.eval_ind_k(art)
   return
   art.dists=[((art.behavior-x.behavior)**2).sum() for x in population]
   arch_dists=[((art.behavior-x.behavior)**2).sum() for x in archive]
   art.dists+=arch_dists
   art.dists.sort()

 def eval_ind_k(self,art):
  global best_evo,best_evo_org,best_fit,best_fit_org
  raw_fitness = fitness_end(art)
  if raw_fitness > self.highest_fitness:
   self.highest_fitness=raw_fitness
   best_fit=self.highest_fitness
   best_fit_org=art.copy()
      

  if (self.do_fitness):
    art.fitness = raw_fitness
  else:  
    nearest,indexes=self.tree.query(art.behavior,NS_K)
    art.fitness=sum(nearest)

 def evolve(self):
  global best_evo,best_evo_org,best_fit,best_fit_org
  repop=0
  while self.evals < self.max_evals: #and not self.solved:
   eflag=False
   #population.sort(key=lambda x:x.fitness,reverse=True)
   self.evals+=1
   if(self.evals%1000==0):
    keys=self.behavior_density.keys()
    #print self.evals,len(keys),calc_population_entropy(self.population),exploration_measure(self)
    quant=self.evals,len(keys),calc_population_entropy(self.population),complexity(self.population),best_fit
    print quant
    log_file.write(str(quant)+"\n")

   if(calc_evo and self.evals%250000==0):
    #run genome in the maze simulator
    print "EVO-CALC"
    for org in random.sample(self.population,200): 
     evo=evo_fnc(org,1000)
     if evo>best_evo:
      best_evo=evo
      best_evo_org=org.copy()
     print "evolvability:", evo
     evo_file.write(str(self.evals)+" "+str(evo)+"\n")
    print "EVO-CALC END"
    evo_file.flush()

   if extinction and self.evals>50 and (self.evals-1)%(interval)==0:
    #survivor_orgs=random.sample(self.population,10)
    survivor_orgs=optimize_pick(self.population,10)
    eflag=True
    repop=len(self.population)-len(survivor_orgs)
    to_delete=[k for k in self.population if k not in survivor_orgs]
    for k in to_delete:
     del k
    self.population=survivor_orgs
   
   if(disp):
    #if eflag:
    #  raw_input()
    render(self.population,self.archive,self.behavior_density)
    #if eflag:
    #  raw_input()
   t_size=5
   parents=random.sample(self.population,t_size)
   parent=reduce(lambda x,y:x if x.fitness>y.fitness else y,parents)
   child=parent.copy()
   child.mutate()
   child.parent=parent
   child.map()

   self.population.append(child)
   self.behavior_density[map_into_grid(child)]+=1

   if(self.evals%50!=0):
    self.eval_ind(child) 
   else:
    self.eval_pop()

   if(child.solution()):
     if not self.solved:
      self.solved=True
      self.solution_eval=self.evals
     self.solution=child
   if(random.random()<0.001):
    self.archive.append(child)

   if repop==0:
    to_kill=random.sample(self.population,t_size)
    to_kill=reduce(lambda x,y:x if x.fitness<y.fitness else y,parents)
    self.population.remove(to_kill)
    del to_kill
   else:
    repop-=1   

  best_evo_org.save(outfile+"_bestevo.dat") 
  best_fit_org.save(outfile+"_bestfit.dat") 
  if self.solved:
   best_fit_org.save(outfile+"_%d_solution.dat" % self.solution_eval)

  return self.solved

if disp:
 import pygame
 from pygame.locals import *
 pygame.init()
 pygame.display.set_caption('Viz')
 screen =pygame.display.set_mode((SZX,SZY))
 
 background = pygame.Surface(screen.get_size())
 background = background.convert()
 background.fill((250, 250, 250))

def render(pop,arc,bd=None):
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

 for robot in arc:
  x=mazepy.feature_detector.endx(robot)*SZX
  y=mazepy.feature_detector.endy(robot)*SZY
  rect=(int(x),int(y),5,5)
  pygame.draw.rect(screen,(0,255,0),rect,0)
 pygame.display.flip()

from entropy import *
evo_fnc = calc_evolvability_cnt


def do_branch_search():
 budget=1000
 branches=1

 evolves=[ss_evolve(do_fit=False,eval_budget=budget) for z in range(branches)]
 it=0
 while True:
  print it
  best_exp=-100000
  best_mod=None
  for k in evolves:
   k.evolve()
   k.explore=exploration_measure(k) 
   print k.explore,k.solved
   if k.explore>best_exp:
    best_exp=k.explore
    best_mod=k
  print "before.."
  evolves=[ss_evolve(do_fit=False,eval_budget=budget,copy=best_mod) for k in evolves]
  print "after.."
  it+=1 
   



def solution_accum():
 n_solutions=[]
 f_solutions=[]
 trials=101
 for z in range(trials):
  k=ss_evolve(do_fit=False,eval_budget=50000)
  k.evolve()
  if (k.solved):
   n_solutions.append(k.solution.get_behavior())
   print z,"solved"
  else:
   print z,"failed"
 
  k=ss_evolve(do_fit=True,eval_budget=50000)
  k.evolve()
  if (k.solved):
   f_solutions.append(k.solution.get_behavior())
   print z,"solved"
  else:
   print z,"failed"

  if z%10==0:
   print "Saving...",z
   a=open("fit_solutions.dat","w")
   pickle.dump(f_solutions,a)
   a.close()
   a=open("nov_solutions.dat","w")
   pickle.dump(n_solutions,a)
   a.close()
 

if(__name__=='__main__'):

 log_file=open(outfile+".log","w")
 evo_file=open(outfile+".evo","w")

 #mazepy.mazenav.initmaze("medium_maze_list.txt","neat.ne")
 mazepy.mazenav.initmaze("hard_maze_list.txt",nefile)
 #mazepy.mazenav.initmaze("medium_maze_list.txt")

 if(seed==-1):
  mazepy.mazenav.random_seed()
 else:
  random.seed(seed)
  mazepy.mazenav.seed(seed)


 robot=None
 #do_branch_search()
 
 #for z in range(10000):
 k=ss_evolve(do_fit=False,eval_budget=6000000,psize=500)
 k.evolve()
