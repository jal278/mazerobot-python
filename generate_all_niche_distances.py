import pdb
import numpy as np
import precomputed_domain
from multiprocessing import Pool
import os
import time


def do_job(x):
 maze,niche = x
 domain_total = precomputed_domain.precomputed_maze_domain(maze)
 domain_total.niche_distance_calculate(niche)
 return 0

if __name__=='__main__':
 maze="medium"
 domain = precomputed_domain.precomputed_maze_domain(maze)
 niches = np.unique( domain.data["behaviorhash"])
 jobs = []

 pdb.set_trace()
 for niche in niches[:10]:
  jobs.append((maze,niche))

 p = Pool(processes=5) 
 p.map(do_job,jobs)

 #set_seeds(1003)