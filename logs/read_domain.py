import numpy as np
import pdb

def read_in(fname='storage.dat'):
 dt = np.dtype([('x', np.uint16), ('y', np.uint16),('evolvability',np.uint16),('behaviorhash',np.uint16)])
 domain = np.fromfile(fname,dt)
 return domain


domain = read_in()
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
