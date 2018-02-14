from precomputed_domain import *
import math

#global display flag
#turn on to visualize search
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

#render function
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

 def __init__(self,domain,pop_size=250,tourn_size=2,elites=1,drift=0.0,fuss=False,mutation_rate=0.8,diversity=0.0,search_mode="fitness",log_evolvability=False):

  self.epoch_count = 0
  self.domain = domain
  self.population = [self.domain.generate_random() for _ in xrange(pop_size)]
  self.pop_size = pop_size
  self.tourn_size = tourn_size 
  self.elites = elites
  self.diversity_pressure = diversity
  self.log_evolvability = log_evolvability

  self.behavior_count=np.zeros(10000) #for counting how many behaviors have been encountered
  
  self.rarity=False
  self.novelty=False
  self.fuss=False
  self.evolvability=False
  self.evo_everywhere=False
  self.evo_steps=1

  self.metrics = metrics(domain)

  if search_mode=='fitness':
   pass
  if search_mode=='rarity':
   self.rarity=True
  if search_mode=='novelty':
    self.novelty=True
  if search_mode=='fuss':
   self.fuss=True
  if search_mode.count('evolvability')>0:
   self.evolvability=True
   if search_mode.count('everywhere')>0:
       self.evo_everywhere=True
   else:
       self.evo_steps=int(search_mode[-1])

  #evaluations spent and solved flag
  self.evals=0
  self.solved=False

  #novelty search specific
  self.archive = np.zeros((MAX_ARCHIVE_SIZE,domain.behavior_size))
  self.archive_size = 0 
  self.archive_ptr = 0

  self.map_evolvability = lambda x:self.map_general(self.domain.evolvability_everywhere,x)
  self.map_fitness = lambda x,y:self.domain.map_fitness(x)

  if self.evolvability:
   if self.evo_everywhere:
       self.domain.everywhere_evolvability_calculate()
       self.map_fitness = lambda x,y:self.map_general(self.domain.evolvability_everywhere,x)
   else:
       self.domain.kstep_evolvability_calculate(self.evo_steps)
       self.map_fitness = lambda x,y:self.map_general(lambda ind:self.domain.evolvability_ks(ind,k=self.evo_steps),x)

  if self.rarity:
   self.map_fitness = lambda x,y:self.map_general(self.metrics.rarity_score,x)
  if self.novelty:
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
  if log_evolvability:
   self.evolvability = self.map_evolvability(self.population)


 def map_general(self,measure,population):
      return np.array([measure(x) for x in population])

 def select_fuss(self,pop):
     rnd_fit = random.uniform(self.min_fit,self.max_fit)
     abs_dif = self.fitness - rnd_fit
     closest_idx = np.argmin(abs_dif)
     if random.random()<self.drift:
        closest_idx = random.randint(0,self.pop_size-1)

     return self.domain.clone(pop[closest_idx])

 def select_diverse(self,pop):
   offs = np.random.randint(0,self.pop_size,4)
   dist = distance_matrix(np.take(pop,offs)).sum(0)
   off = offs[np.argmax(dist)]
   return self.domain.clone(pop[off])

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

  diversity_pressure=self.diversity_pressure 
  for _ in xrange(self.pop_size-elites):
   if random.random()<diversity_pressure:
    child = self.select_diverse(pop)
   else:
    child = self.selection_mechanism(pop)

   if random.random()<self.mutation_rate:
    child = self.domain.mutate(child) 

   newpop.append(child)

  return newpop

 def hillclimb(self,eval_budget,shadow=False):
  champ = self.population[0]
  champ_fitness = self.map_fitness([champ],None)[0]
  orig_fitness = champ_fitness
  selections = 0
  solved=False
  for _ in xrange(eval_budget):
   offspring = self.domain.clone(champ)
   offspring = self.domain.mutate(offspring)

   offspring_fitness = self.map_fitness([offspring],None)[0]
   solution = self.domain.map_solution([offspring])[0]
   if shadow:
       champ=offspring

   if solution:
       print "solved"
       solved=True

   if offspring_fitness > champ_fitness:
       champ_fitness = offspring_fitness
       champ = offspring
       print _,champ_fitness
       selections+=1

  return orig_fitness,champ_fitness,selections,solved
  
 def epoch(self,count_behaviors=True):
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

  if count_behaviors:
   self.behaviorhash = self.domain.map_behaviorhash(self.population)
   np.add.at(self.behavior_count,self.behaviorhash,1)

  if (self.solutions.sum()>0):
   champ = np.argmax(self.solutions)
   #print self.gt_fitness[np.argmax(self.solutions)]
   self.solved=True
   return True 

  #print distance_matrix(self.population).sum()

  #print self.evolvability.max(),self.evolvability.mean(),self.evolvability.min() 
  if self.best_gt < self.gt_fitness.max():
   self.best_gt = self.gt_fitness.max()
   print self.epoch_count,self.best_gt

def repeat_search_rarity(generator,times,seeds=None,gens=250):
 solved=[]
 evals=[]
 data=np.zeros((times,gens))
 if seeds==None:
     seeds=range(1,times+1)
 for x in range(times):
  set_seeds(seeds[x])
  search=generator()

  for _ in xrange(gens):
   if _%100==0:
    print _*search.pop_size
   sol = search.epoch()
   #if sol:
   # print "solved" 
   # break
   rarity= np.array(search.map_general(search.metrics.rarity_score,search.population))
   data[x,_] = rarity.max() 
  print search.solved
  if search.solved:
      solved.append(True)
      evals.append(search.evals)
  else:
      solved.append(False)
      evals.append(-1)
 return data

def repeat_search_evolvability(generator,times,seeds=None,gens=250):
 solved=[]
 evals=[]
 data=np.zeros((times,gens))
 if seeds==None:
     seeds=range(1,times+1)
 for x in range(times):
  set_seeds(seeds[x])
  search=generator()

  for _ in xrange(gens):
   if _%100==0:
    print _*search.pop_size
   sol = search.epoch()
   #if sol:
   # print "solved" 
   # break
   evolvability = np.array(search.map_general(lambda ind:search.domain.evolvability_everywhere(ind),search.population))
   data[x,_] = evolvability.max() 
  print search.solved
  if search.solved:
      solved.append(True)
      evals.append(search.evals)
  else:
      solved.append(False)
      evals.append(-1)
 return data


def repeat_search_count_behaviors(generator,times,seeds=None,gens=250):
 solved=[]
 evals=[]
 total_behaviors=np.zeros((times,gens))
 if seeds==None:
     seeds=range(1,times+1)
 for x in range(times):
  set_seeds(seeds[x])
  search=generator()

  for _ in xrange(gens):
   if _%100==0:
    print _*search.pop_size
   sol = search.epoch()
   #if sol:
   # print "solved" 
   # break
   total_behaviors[x,_] = (search.behavior_count>0).sum() 
  print search.solved
  if search.solved:
      solved.append(True)
      evals.append(search.evals)
  else:
      solved.append(False)
      evals.append(-1)
 return total_behaviors

def repeat_search(generator,times,seeds=None,gens=250):
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
 maze = 'medium'
 domain = precomputed_maze_domain(maze,storage_directory="logs/",mmap=True)

 rarity = lambda : search(domain,search_mode="rarity",pop_size=500,tourn_size=2)
 evo1 = lambda : search(domain,search_mode="evolvability1",pop_size=500)
 evo2 = lambda : search(domain,search_mode="evolvability2",pop_size=500)
 evo3 = lambda : search(domain,search_mode="evolvability3",pop_size=500)
 evo4 = lambda : search(domain,search_mode="evolvability4",pop_size=500)
 evo_ev = lambda : search(domain,search_mode='evolvability_everywhere',pop_size=500)

 nov = lambda : search(domain,search_mode="novelty",tourn_size=2,pop_size=500) #was 0.25
 fit = lambda : search(domain,tourn_size=2,pop_size=500)
 rnd = lambda : search(domain,tourn_size=3,pop_size=500,drift=1.0,elites=0)
 
 search = rarity()

 for _ in xrange(1000):
  if _%100==0:
   print _*search.pop_size
  sol = search.epoch()
  if sol:
    print "solved" 
    break
  if(disp):
    render(search,domain)
 print search.evals

