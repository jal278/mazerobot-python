import random
import numpy as np
import pdb
from scipy.spatial import cKDTree as kd

def evalNovKDTree(data,archive):
  tot_data = np.vstack( (data,archive) )
  tree=kd(tot_data) 
  
  nov = np.zeros(data.shape[0])
  for idx in xrange(data.shape[0]):
   nov[idx]=eval_ind_k(tree,data[idx])

  return nov
 
def eval_ind_k(tree,pt,NS_K=20):
 nearest,indexes=tree.query(pt,NS_K)
 return sum(nearest)

class precomputed_maze_domain:
  def __init__(self):
    self.data = self.read_in()
    self.size = 16
    self.behavior_size = 2

  def read_in(self,fname='storage.dat'):
   dt = np.dtype([('x', np.uint16), ('y', np.uint16),('evolvability',np.uint16),('behaviorhash',np.uint16)])
   domain = np.fromfile(fname,dt)
   return domain
 
  def to_idx(self,descriptor):
   idx = 0
   for val in descriptor:
    idx*=3
    idx+=val%3
   return idx

  def from_idx(self,idx):
   out = np.zeros(self.size)
   for _ in xrange(self.size-1,-1,-1):
    out[_] = idx%3
    idx/=3 
   return out  

  def get_data(self,descriptor=None,idx=None):
   if idx==None:
    idx=self.to_idx(descriptor)

   return self.data[idx] 

  def clone(self,descriptor):
   return descriptor.copy()

  def mutate(self,descriptor):
   idx = np.random.randint(0,self.size-1)
   descriptor[idx] = np.random.randint(-1,2)
   return descriptor 

  def fitness(self,descriptor):
   #return sum(descriptor)
   x,y,_,_ = self.get_data(descriptor=descriptor)

   return -(float(x-32)**2+float(y-20)**2)

  def map_gt_fitness(self,population):
   return np.array([self.fitness(x) for x in population])

  def map_novelty(self,population,archive):
   behavior_vec = self.map_behavior(population)
   nov = evalNovKDTree(behavior_vec,archive)
   return nov

  def map_fitness(self,population):
   return np.array([self.fitness(x) for x in population])

  def map_behavior(self,population):
   idxes = [self.to_idx(x) for x in population]
   x=self.data['x'][idxes]
   y=self.data['y'][idxes]
   t= np.transpose(np.vstack([x,y]))
   return t

  def behavior(self,descriptor):
   x,y = self.get_data(descriptor=descriptor)[:2]
   return x,y

  def generate_random(self):
   return np.random.randint(-1,2,self.size)

MAX_ARCHIVE_SIZE = 1000
class search:
 def __init__(self,domain,pop_size=500,novelty=True):
  self.epoch_count = 0
  self.domain = domain
  self.population = [self.domain.generate_random() for _ in xrange(pop_size)]
  self.pop_size = pop_size

  self.archive = np.zeros((MAX_ARCHIVE_SIZE,domain.behavior_size))
  self.archive_size = 0 

  self.map_fitness = lambda x,y:self.domain.map_fitness(x)
  if novelty:
   self.map_fitness = lambda x,y:self.domain.map_novelty(x,y)

  self.map_gt_fitness = lambda x,y:self.domain.map_fitness(x)

  self.mutation_rate = 0.5
  self.best_gt = -1e10

  self.fitness = self.map_fitness(self.population,self.archive[:self.archive_size])

 def select(self,pop):
  elites=1
  champ_idx = np.argmax(self.fitness)
  newpop = []

  #elitism
  for _ in xrange(elites):
   newpop.append(self.domain.clone(pop[champ_idx]))
  
  tourn_size = 2
  #simple tournament selection n=2
  for _ in xrange(self.pop_size-elites):
   offs = np.random.randint(0,self.pop_size,tourn_size)
   fits = self.fitness[offs]

   off = offs[np.argmax(fits)]
   child = self.domain.clone(pop[off])

   if random.random()<self.mutation_rate:
    child = self.domain.mutate(child) 

   newpop.append(child)

  return newpop

 def epoch(self):
  self.epoch_count+=1
  new_population = self.select(self.population)

  self.archive[self.archive_size] = self.domain.map_behavior([random.choice(self.population)])[0]
  self.archive_size+=1

  self.population = new_population
  self.fitness = self.map_fitness(self.population,self.archive[:self.archive_size]) 
  self.gt_fitness = self.map_gt_fitness(self.population,None)
 
  if self.best_gt < self.gt_fitness.max():
   self.best_gt = self.gt_fitness.max()
   print self.epoch_count,self.best_gt
  #print self.fitness.mean(),self.fitness.max()
 
domain_total = precomputed_maze_domain()

search = search(domain_total)
for _ in xrange(1000):
 search.epoch()

"""
test_idx = 2 #138976

assert domain_total.to_idx(domain_total.from_idx(test_idx)) == test_idx

domain = domain_total.data
heat_map = np.zeros([210,210])
heat_map[domain['x'],domain['y']]+=1

#fitness = np.sqrt((domain['x']-32)**2 +(domain['y']-20)**2)

x=np.array(domain['x'],dtype=float)
y=np.array(domain['y'],dtype=float)

dx=(x-32)**2 
dy=(y-20)**2
fitness = np.sqrt(dx+dy)
idx = np.argmin(fitness)

print fitness[idx],domain['x'][idx],domain['y'][idx]

pdb.set_trace()
import matplotlib
matplotlib.use('agg')
from pylab import *
imshow(heat_map)
savefig("out.png")

pdb.set_trace()
"""
