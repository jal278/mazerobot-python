from precomputed_domain import *
import pickle
import pdb

if __name__=='__main__': 
 maze="medium"
 domain = precomputed_maze_domain(maze,storage_directory="logs/",mmap=True)
 calc_obj = metrics(domain)
 rarity = calc_obj.rarity()

 individual = random.randint(0,3**16-1)
 behavior = domain.data["behaviorhash"][individual]
 individual_rarity = rarity[behavior]

 neighbors = domain.data["behaviorhash"][domain.get_neighbors(individual)]
 neighbor_rarity = [rarity[b] for b in domain.data["behaviorhash"][neighbors]]

 print individual_rarity,neighbor_rarity
 asfd

 import time
  
 #print repeat_search(fit_loose,50)
 #afsd
 if True:
  methods = {'nov':nov,'fit':fit,'rnd':rnd}
  res = {}
 
  before=time.time()
  for method in methods:
   #print repeat_search(rnd,5,range(1,6))
   res[method] = repeat_search(methods[method],100)
  after=time.time()
  pdb.set_trace()
  import pickle
  outfile = open("medresults.pkl","w")
  pickle.dump(res,outfile)
  fasd

 #set_seeds(1003)
 search = search(domain_total,novelty=False,tourn_size=2,pop_size=500,drift=0.0,diversity=0.75,elites=5)
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

