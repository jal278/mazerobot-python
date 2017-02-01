from precomputed_domain import *

#global display flag
disp=False

#display depends upon pygame
if disp:
 SZX=SZY=400
 import pygame
 from pygame.locals import *
 pygame.init()
 pygame.display.set_caption('Viz')
 screen =pygame.display.set_mode((SZX,SZY))
 
 background = pygame.Surface(screen.get_size())
 background = background.convert()
 background.fill((250, 250, 250,255))

#redner function
def render(search,domain):
 global screen,background
 pop = search.population
 novelty = search.novelty
 archive = search.archive
 screen.blit(background, (0, 0))

 mn_fit = search.fitness.min()
 mx_fit = search.fitness.max()

 for idx,robot in enumerate(pop):
  x,y = domain.norm_behavior(robot)
  
  x=x*SZX
  y=y*SZY
  rect=(int(x),int(y),5,5)
  col = (search.fitness[idx]-mn_fit)/(mx_fit-mn_fit)*255.0
  col = int(col)
  pygame.draw.rect(screen,col,rect,0)

 if novelty:
  for robot in archive:
   x,y = robot/300
   x=x*SZX
   y=y*SZY
   rect=(int(x),int(y),5,5)
   pygame.draw.rect(screen,(0,255,0),rect,0)

 pygame.display.flip()

#general search class 
MAX_ARCHIVE_SIZE = 1000
class search:

 def __init__(self,domain,pop_size=500,novelty=False,tourn_size=2,elites=1,evolvability=False,drift=0.0,fuss=False,mutation_rate=0.8):
  self.epoch_count = 0
  self.domain = domain
  self.population = [self.domain.generate_random() for _ in xrange(pop_size)]
  self.pop_size = pop_size
  self.tourn_size = tourn_size 
  self.elites = elites
  
  self.fuss = fuss

  self.evals=0
  self.solved=False

  self.novelty = novelty
  self.archive = np.zeros((MAX_ARCHIVE_SIZE,domain.behavior_size))
  self.archive_size = 0 
  self.archive_ptr = 0

  self.map_evolvability = self.domain.map_evolvability
  
  self.map_fitness = lambda x,y:self.domain.map_fitness(x)

  if evolvability:
   self.map_fitness = lambda x,y:self.domain.map_evolvability(x,ks=4) 

  if novelty:
   self.map_fitness = lambda x,y:self.domain.map_novelty(x,y)

  self.map_gt_fitness = lambda x,y:self.domain.map_fitness(x)

  self.mutation_rate = mutation_rate
  self.drift = drift
  self.best_gt = -1e10

  if self.fuss:
      self.selection_mechanism = lambda x:self.select_fuss(x)
  else:
      self.selection_mechanism = lambda x:self.select_tourn(x)

  self.fitness = self.map_fitness(self.population,self.archive[:self.archive_size])
  self.evolvability = self.map_evolvability(self.population)

 def select_fuss(self,pop):
     rnd_fit = random.uniform(self.min_fit,self.max_fit)
     abs_dif = self.fitness - rnd_fit
     closest_idx = np.argmin(abs_dif)
     if random.random()<self.drift:
        closest_idx = random.randint(0,self.pop_size-1)

     return self.domain.clone(pop[closest_idx])

 def select_tourn(self,pop):
   offs = np.random.randint(0,self.pop_size,self.tourn_size)
   fits = self.fitness[offs]
   if random.random()<self.drift:
       off = random.randint(0,self.pop_size-1)
   else:
       off = offs[np.argmax(fits)]
   return self.domain.clone(pop[off])

 def select(self,pop):
  elites=self.elites
  champ_idx = np.argmax(self.fitness)
  newpop = []

  #elitism
  for _ in xrange(elites):
   newpop.append(self.domain.clone(pop[champ_idx]))
  
  self.min_fit = self.fitness.min()
  self.max_fit = self.fitness.max()

  for _ in xrange(self.pop_size-elites):
   child = self.selection_mechanism(pop)

   if random.random()<self.mutation_rate:
    child = self.domain.mutate(child) 

   newpop.append(child)

  return newpop

 def epoch(self):
  self.epoch_count+=1
  self.evals+=self.pop_size
  new_population = self.select(self.population)

  for _ in xrange(1):
   if self.archive_ptr>=MAX_ARCHIVE_SIZE:
    self.archive_ptr = self.archive_ptr % MAX_ARCHIVE_SIZE
   self.archive[self.archive_ptr] = self.domain.map_behavior([random.choice(self.population)])[0]

   if self.archive_size<MAX_ARCHIVE_SIZE:
    self.archive_size+=1

   self.archive_ptr+=1
   
  self.population = new_population
  self.fitness = self.map_fitness(self.population,self.archive[:self.archive_size]) 
  self.gt_fitness = self.map_gt_fitness(self.population,None)
  #self.evolvability = self.map_evolvability(self.population)
  self.solutions = self.domain.map_solution(self.population)

  if (self.solutions.sum()>0):
   champ = np.argmax(self.solutions)
   print self.gt_fitness[np.argmax(self.solutions)]
   self.solved=True
   return True 

  #print distance_matrix(self.population).sum()

  #print self.evolvability.max(),self.evolvability.mean(),self.evolvability.min() 
  if self.best_gt < self.gt_fitness.max():
   self.best_gt = self.gt_fitness.max()
   print self.epoch_count,self.best_gt

def repeat_search(generator,times,seeds=None,gens=500):
 solved=[]
 evals=[]
 if seeds==None:
     seeds=range(1,times+1)
 for x in range(times):
  set_seeds(seeds[x])
  search=generator()

  for _ in xrange(gens):
   if _%100==0:
    print _*search.pop_size
   sol = search.epoch()
   if sol:
    print "solved" 
    break
  print search.solved
  if search.solved:
      solved.append(True)
      evals.append(search.evals)
  else:
      solved.append(False)
      evals.append(-1)
 return solved,evals

if __name__=='__main__': 

 domain_total = precomputed_maze_domain("hard",storage_directory="logs/",mmap=True)

 nov = lambda : search(domain_total,novelty=True,tourn_size=2,pop_size=500,drift=0.25)
 fit_loose = lambda : search(domain_total,novelty=False,tourn_size=3,pop_size=500,drift=0.85,elites=5) 
 fit = lambda : search(domain_total,novelty=False,tourn_size=3,pop_size=500)
 rnd = lambda : search(domain_total,tourn_size=3,pop_size=500,drift=1.0,elites=0)
 import time

 methods = {'nov':nov,'fit':fit,'fit_loose':fit_loose,'rnd':rnd}
 res = {}
 
 before=time.time()
 for method in methods:
  #print repeat_search(rnd,5,range(1,6))
  res[method] = repeat_search(methods[method],50)
 after=time.time()
 pdb.set_trace()
 import pickle
 outfile = open("hardresults.pkl","w")
 pickle.dump(res,outfile)
 fasd

 #set_seeds(1003)
 search = search(domain_total,novelty=False,tourn_size=3,pop_size=500,drift=0.8,elites=5)
 #search = search(domain_total,novelty=True,tourn_size=2,pop_size=250,drift=0.25,evolvability=False)
  
 for _ in xrange(1000):
  if _%100==0:
   print _*search.pop_size
  sol = search.epoch()
  if sol:
   print "solved" 
   break
  if(disp):
   render(search,domain_total)
 print search.evals

