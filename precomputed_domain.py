import time
import random
import numpy as np
import pdb
import os.path
import pickle
from scipy.spatial import cKDTree as kd
from numba import jit,jitclass

#kdtree calculation for fast novelty search evaluation
@jit
def evalNovKDTree(data,archive):
  tot_data = np.vstack( (data,archive) )
  tree=kd(tot_data) 
  
  nov = np.zeros(data.shape[0])
  for idx in xrange(data.shape[0]):
   nov[idx]=eval_ind_k(tree,data[idx])

  return nov
 
#evaluate an individual using a precalculated kdtree
def eval_ind_k(tree,pt,NS_K=20):
 nearest,indexes=tree.query(pt,NS_K)
 return sum(nearest)

#optimized neighbor-gathering function
@jit
def _get_neighbors(idx,size=16):
   n = np.zeros(3*size,dtype=np.int64)
   leading = idx
   discarded = 0 
   cnt=0
   for it in range(size):
    digit = leading%3
    leading -= digit

    for permut in range(3):
     n[cnt]= (leading+permut)*(3**it) + discarded 
     cnt+=1

    discarded += digit*(3**it)
    leading/=3 

   #print self.from_idx(idx)
   #for n_idx in n:
   # print self.from_idx(n_idx) 
   return n

@jit
def _add_to_neighbors(idx,n,cnt,size=16):
   leading = idx
   discarded = 0 
   for it in range(size):
    digit = leading%3
    leading -= digit

    for permut in range(3):
     n[cnt]= (leading+permut)*(3**it) + discarded 
     cnt+=1

    discarded += digit*(3**it)
    leading/=3 
   return cnt 

@jit
def _get_evo(idx,behavior,steps=3,size=16):
 sz = 0
 for x in range(steps+1):
  sz+= (3*size)**x
 
 n=np.zeros( sz,dtype=np.int64)

 n[0]=idx
 cnt = 1
 cnt_old = 0
 for step in xrange(steps):
  cnt_cached = cnt
  for genome in xrange(cnt_old,cnt):
   cnt = _add_to_neighbors(n[genome],n,cnt)
  cnt_old = cnt_cached
  #print cnt-cnt_old 
  #print n.shape
 total_idxes = n
 return np.unique(behavior[total_idxes]).shape

@jit
def gather_neighbors(olist):
   neighbors=np.zeros_like(olist,dtype=np.uint8)
   idxes = olist.nonzero()[0]
   neighbors[idxes]=1
   for idx in idxes:
    neighbors[_get_neighbors(idx)]=1
   return neighbors

@jit
def distance(g1,g2):
    dist = np.abs(g1-g2).sum()
    return dist

@jit
def nstep_evo(idx,behaviorhash,n):
   onehot = np.zeros_like(behaviorhash)
   onehot[idx]=1
   dists= _solution_distance_calculate(onehot,max_distance=n,verbose=False)
   reachable = (dists<=n).nonzero()
   behaviors = np.unique(behaviorhash[reachable])
   return behaviors.shape

@jit(["uint8[:](uint8[:],int64,int16)"])
def _solution_distance_calculate(solutions,max_distance=1000,verbose=False):
   DUMMY_VAL = 10000.0
   distances = np.ones(solutions.shape[0],dtype=np.uint8)*DUMMY_VAL
   distances[solutions==1] = 0
   
   open_list = np.zeros(len(distances),dtype=np.uint8) 
   open_list[(distances<DUMMY_VAL)]=1
   closed_list = np.zeros(len(distances),dtype=np.uint8)

   cost = 1
   while open_list.sum()>0 and cost<=max_distance:
    #gather neighbors from open list
    neighbors = gather_neighbors(open_list)
    #mark everything in open list as closed
    closed_list[open_list==1] = 1
    #clear open list
    open_list[:]=0

    #disregard neighbors already explored
    neighbors[(closed_list==1)] = 0
    #set cost for remaining neighbors
    distances[(neighbors==1)]=cost

    open_list[(neighbors==1)]=1
    cost+=1
    if verbose:
     print cost 
    if cost>20:
     break
   return distances 

@jit
def _to_idx(descriptor):
   idx = 0
   for val in descriptor:
    idx*=3
    idx+=val%3
   return int(idx)

@jit
def _from_idx(idx,size=16):
   out = np.zeros(size)
   for _ in xrange(size-1,-1,-1):
    out[_] = idx%3
    idx/=3 
   return out  

@jit
def _get_data(descriptor,data):
   #if idx==None:
   idx=_to_idx(descriptor)
   return data[idx] 

#class to hold metrics
class metrics:
  def __init__(self,domain):
      self.domain = domain
      self.rarity()

  def rarity(self):
   rarity_file = "rarity_%s.pkl"%self.domain.maze
   print rarity_file
   if os.path.isfile(rarity_file):
    print "rarity cached..."
    ifile=open(rarity_file)
    rarity=pickle.load(ifile)
   else:
    print "calculting rarity..."
    rarity={}
    for niche in np.unique(self.domain.data["behaviorhash"]):
     rarity[niche]=(self.domain.data["behaviorhash"]==niche).sum()
     print niche,rarity[niche]
    ofile = open(rarity_file,"w")
    pickle.dump(rarity,ofile)
   self.rarity=rarity
   return rarity

  def rarity_score(self,ind):
   return -self.rarity[self.domain.data["behaviorhash"][self.domain.to_idx(ind)]]  

class precomputed_maze_domain:
  def __init__(self,maze="hard",storage_directory="~/evodata/logs",mmap=False):
    self.maze= maze
    self.storage_directory = storage_directory
    self.data = self.read_in( ("%s/storage_"%storage_directory)+maze+".dat" )
    self.size = 16
    self.behavior_size = 2  
    self.solution_distance_calculate()
    self.niche_distance = {}
    self.evo = {}
    self.evo_everywhere=None
    self.mmap=mmap

    if maze=='hard':
     self.goal=(31,20)
    if maze=='medium':
     self.goal=(270,100)

  def read_in(self,fname='storage.dat'):
   self.fname = fname
   dt = np.dtype([('x', np.uint16), ('y', np.uint16),('evolvability',np.uint16),('behaviorhash',np.uint16),('solution',np.uint8)])
   domain = np.fromfile(fname,dt)
   return domain

  def random_idx(self):
   return random.randint(0,3**16-1)

  def get_neighbors(self,idx):
   n = []
   leading = idx
   discarded = 0 

   for it in range(self.size):
    digit = leading%3
    leading -= digit

    for permut in range(3):
     n.append( (leading+permut)*(3**it) + discarded )

    discarded += digit*(3**it)
    leading/=3 

   return n

  def gather_neighbors(self,olist):
   neighbors=np.zeros_like(olist,dtype=np.uint8)
   idxes = olist.nonzero()[0]
   neighbors[idxes]=1
   for idx in idxes:
    neighbors[self.get_neighbors(idx)]=1
   return neighbors
 
  def niche_distance_calculate(self,niche=0):
   solution_file = self.fname+".niche%d.npy"%niche
   cached_solutions = os.path.isfile(solution_file)

   mmap=None
   if self.mmap==True: 
    mmap='r+'

   if not cached_solutions:
    print "not cached..."
    data = self.data['behaviorhash']==niche
    self.niche_distance[niche] = _solution_distance_calculate(data).astype(np.uint8)
    np.save(solution_file,self.niche_distance[niche])
    del self.niche_distance[niche]
   
    self.niche_distance[niche] = np.load(solution_file,mmap_mode=mmap)
   else:
    print "cached..."
    
    self.niche_distance[niche] = np.load(solution_file,mmap_mode=mmap)

  def load_all_niche_distances(self):
   niches = np.unique( self.data["behaviorhash"])
   for niche in niches:
    self.niche_distance_calculate(niche)

  def kstep_evolvability_calculate(self,k):
   if k in self.evo:
       return

   evo_file = self.fname+".evo%d.npy"%k
   cached_solutions = os.path.isfile(evo_file) 
   if not cached_solutions:
    print "not cached..."  

    self.load_all_niche_distances()
    niche_distance = self.niche_distance.values()
    self.evo[k] = _kstep_evolvability_calculate(niche_distance,k)
    self.evo[k] = self.evo[k].astype(np.uint16)
    np.save(evo_file,self.evo[k])
   else:
    print "cached..."
    self.evo[k]= np.load(evo_file)

  def everywhere_evolvability_calculate(self):
   if self.evo_everywhere!=None:
       return

   evo_file = self.fname+".evoall.npy"
   cached_solutions = os.path.isfile(evo_file) 
   if not cached_solutions:
    print "not cached..."  
    self.load_all_niche_distances()
    niche_distance = self.niche_distance.values()
    self.evo_everywhere  = _everywhere_evolvability_calculate(niche_distance)
    self.evo_everywhere =  self.evo_everywhere.astype(np.float32)
    np.save(evo_file,self.evo_everywhere)

   else:
    print "cached..."
    self.evo_everywhere = np.load(evo_file)

  def solution_distance_calculate(self):
   solution_file = self.fname+".solutions.npy"
   cached_solutions = os.path.isfile(solution_file)
   
   if not cached_solutions:
    print "not cached..."
    data = self.data['solution']
    self.distance= _solution_distance_calculate(data)
    self.distance=self.distance.astype(np.uint8)
    np.save(solution_file,self.distance)
   else:
    print "cached..."
    self.distance= np.load(solution_file)

   """
   DUMMY_VAL = 10000.0
   distances = np.ones(self.data.shape[0])*DUMMY_VAL
   solutions = self.data['solution']
   distances[solutions==1] = 0

   self.open_list = np.zeros(len(distances),dtype=np.uint8) 
   self.open_list[(distances<DUMMY_VAL)]=1
   self.closed_list = np.zeros(len(distances),dtype=np.uint8)

   cost = 1
   while sum(self.open_list)>0:
    #gather neighbors from open list
    neighbors = self.gather_neighbors(self.open_list)
    #mark everything in open list as closed
    self.closed_list[self.open_list==1] = 1
    #clear open list
    self.open_list[:]=0

    #disregard neighbors already explored
    neighbors[(self.closed_list==1)] = 0
    #set cost for remaining neighbors
    distances[(neighbors==1)]=cost

    self.open_list[(neighbors==1)]=1
    cost+=1
    print cost 
    if cost>20:
     break
  """ 

  def to_idx(self,descriptor):
   return _to_idx(descriptor)

  def from_idx(self,idx):
   return _from_idx(idx,self.size)

  def get_data(self,descriptor=None):
   return _get_data(descriptor,self.data)

  def clone(self,descriptor):
   return descriptor.copy()

  def mutate(self,descriptor):
   idx = np.random.randint(0,self.size-1)
   descriptor[idx] = np.random.randint(-1,2)
   return descriptor 

  def evolvability_everywhere(self,descriptor):
   idx = _to_idx(descriptor)
   return -self.evo_everywhere[idx]

  def evolvability_ks(self,descriptor,k):
   idx = _to_idx(descriptor)
   return self.evo[k][idx]

  def evolvability(self,descriptor):
   _,_,evo,_,_ = self.get_data(descriptor=descriptor)
   return evo
   
  def fitness(self,descriptor):
   #return sum(descriptor)
   x,y,_,_,_ = self.get_data(descriptor=descriptor)
   return -(float(x-self.goal[0])**2+float(y-self.goal[1])**2)

  def map_evolvability(self,population,ks=False):
   #return np.array([self.evolvability_ev(x) for x in population])   
   if ks !=False:
    return np.array([self.evolvability_ks(x,ks) for x in population])   
   return np.array([self.evolvability(x) for x in population])   

  def map_gt_fitness(self,population):
   return np.array([self.fitness(x) for x in population])

  def map_novelty(self,population,archive):
   behavior_vec = self.map_behavior(population)
   nov = evalNovKDTree(behavior_vec,archive)
   return nov

  def map_fitness(self,population):
    idxes = [self.to_idx(x) for x in population]
    x=self.data['x'][idxes].astype(np.float32)
    y=self.data['y'][idxes].astype(np.float32)
    return -((x-self.goal[0])**2 + (y-self.goal[1])**2) #np.array([self.fitness(x) for x in population])

  def map_behaviorhash(self,population):
   idxes = [self.to_idx(x) for x in population]
   return self.data['behaviorhash'][idxes]

  def map_behavior(self,population):
   idxes = [self.to_idx(x) for x in population]
   x=self.data['x'][idxes]
   y=self.data['y'][idxes]
   t= np.transpose(np.vstack([x,y]))
   return t

  def behavior(self,descriptor):
   x,y = self.get_data(descriptor=descriptor)[:2]
   return x,y

  def norm_behavior(self,descriptor):
   idx = self.to_idx(descriptor)
   x,y = self.data['x'][idx],self.data['y'][idx] #get_data(descriptor=descriptor)[:2]
   return x/300.0,y/300.0

  def map_solution(self,population):
   return self.data['solution'][ [self.to_idx(x) for x in population] ]

  def generate_random(self):
   return np.random.randint(-1,2,self.size)



class precomputed_maze_individual:
  def __init__(self,domain):
   self.domain = domain
   self.idx = 0
   self.descriptor = None

  def init_rand(self):
   self.idx = self.domain.random_idx()
   self.descriptor = self.domain.from_idx(self.idx)

  def mutate(self):
   self.descriptor = self.domain.mutate(self.descriptor)
   self.idx = self.domain.to_idx(self.descriptor)

  def map(self):
   row = self.domain.data[self.idx]
   self.behavior = row[0]/300.0,row[1]/300.0
   self._solution = row[-1]
   self.fitness = self.domain.fitness(self.descriptor)

  def solution(self):
   return self._solution

  def copy(self):
   c = precomputed_maze_individual(self.domain)
   c.idx = self.idx
   c.descriptor = self.descriptor
   return c 

class precomputed_domain_interface():
 def __init__(self,path="logs/storage.dat"):
   self.precompute = precomputed_maze_domain(path,storage_directory="./logs")
   self.generator = lambda:precomputed_maze_individual(self.precompute)
   self.get_behavior = lambda x:x.behavior
   self.get_fitness = lambda x:x.fitness 

def set_seeds(x):
 random.seed(x)
 np.random.seed(x)

@jit
def _do_nstep_evo(rng1,rng2,behavior,steps):
 for z in xrange(rng1,rng2):
  out = _get_evo(z,behavior,steps)

evo_distribution = None
@jit
def evolvability_distribution(idx,niche_distance,evo_distribution):
 for k in xrange(len(niche_distance)):
  evo_distribution[k] = niche_distance[k][idx]

def _kstep_evolvability_accum(evo,niche,k):
 lt = ((niche<=k)).astype(np.uint16)
 evo += lt

def _kstep_evolvability_calculate(niche_distance,k):
 sz = niche_distance[0].shape[0]
 evo = np.zeros(sz,dtype=np.uint16)
 for _,niche in enumerate(niche_distance):
  _kstep_evolvability_accum(evo,niche,k)
  print _,evo.max()
 return evo

def _everywhere_evolvability_calculate(niche_distance):
 sz = niche_distance[0].shape[0]
 evo = np.zeros(sz,dtype=np.uint16)
 for _,niche in enumerate(niche_distance):
  evo += niche
  print _,evo.min()
 return evo/float(len(niche_distance))

#testing efficiency of calculating evolvability distribution
def stress_test_evo_dist(amt,niche_distance,niches):
 global evo_distribution
 evo_distribution = np.zeros(len(niches))

 before=time.time()
 x=0
 niche_labels = niche_distance.keys()
 niche_distance = niche_distance.values()
 pdb.set_trace()
 for x in xrange(amt):
  evolvability_distribution(x,niche_distance,evo_distribution)
  x+=1
 after=time.time()
 print after-before



if __name__=='__main__': 
 #set_seeds(1003)

 maze="hard"
 domain_total = precomputed_maze_domain(maze,storage_directory="logs/",mmap=True)

 compute_evolvability=True
 if compute_evolvability:
  for k in range(1,9):
   domain_total.kstep_evolvability_calculate(k)
  domain_total.everywhere_evolvability_calculate()

 search = search(domain_total,novelty=False,tourn_size=2,pop_size=250,evolvability=False)

 for _ in xrange(1000):
  if _%100==0:
   print _*search.pop_size
  sol = search.epoch()
  if sol:
   print "solved" 
   break

 
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


