import matplotlib
matplotlib.use('tkagg')

import mazepy
import random

from grid import q_func_lookup,qagent,q_func_ann 

def process_walls(a):
 segs=[]
 walls=a.get_walls()
 #print len(walls)
 for k in range(0,len(walls),4):
  wall = walls[k:k+4]
  seg=[]
  seg.append((wall[0],wall[1]))
  seg.append((wall[2],wall[3]))
  segs.append(seg)
 return segs

def get_wall_range(walls):
 xcoords1=[seg[0][0] for seg in walls]
 xcoords2=[seg[1][0] for seg in walls]
 ycoords1=[seg[0][1] for seg in walls]
 ycoords2=[seg[1][1] for seg in walls]
 xcoords=xcoords1+xcoords2
 ycoords=ycoords1+ycoords2
 return (min(xcoords),max(xcoords),min(ycoords),max(ycoords))

class mazerobot_world:
 def __init__(self,discrete=False):
  self.episodes=-1
  self.episodeLength=0
  self.maxEpisodeLength=400
  self.maze = mazepy.mazewrapper()
  self.maze.load_env("medium_maze.txt")
  self.reset()
  self.walls = process_walls(self.maze)
  self.wall_range = get_wall_range(self.walls)
  self.discrete=discrete

 def get_actions(self):
   return range(9)

 def reset(self):
   self.episodes+=1
   self.episodeLength=0
   self.maze.reset()
 
 def get_state(self):
   state= list(self.maze.get_state())
   return tuple(state)
 
 """
 def get_behavior(self):
  behavior = list(self.maze.get_behavior())
  behavior[0] /= self.wall_range[1]
  behavior[1] /= self.wall_range[3]
  behavior[2] /= 360.0

  if self.discrete:
   behavior = [round(k,1) for k in behavior]

  return tuple(behavior)
 """

 def perf(self):
  return self.maze.goal_dist()

 def take_action(self,act):
  repeat=5
  for k in xrange(repeat):
   self.maze.take_action(act)
   self.episodeLength+=1

  if self.maze.goal_dist() < 10:
     print "discovered"
     return 100.0,True 

  if self.episodeLength >= self.maxEpisodeLength:
     perf = -self.perf()
     self.reset()
     return perf,True

  return -self.perf(),False

import pylab as pl
from matplotlib import collections as mc
pl.ion()
pl.plot([0,1])
pl.draw()

def vis_rollout(agent,rollouts,timesteps):
 #print  len(agent.q_func.q_table)
 pl.clf()
 ax=pl.gca()
 world=mazerobot_world()
 
 segs=process_walls(world.maze)
 lc = mc.LineCollection(segs)
 ax.add_collection(lc)
 ax.autoscale()

 x=[]
 y=[]
 perfs=[]
 agent.learning=False

 for ep in range(rollouts):
  world.reset()

  for _ in xrange(timesteps-1):
   obs=world.get_state()
   action = agent.act(obs,0,False)
   world.take_action(action)
   behavior = world.maze.get_behavior()
   x.append(behavior[0])
   y.append(behavior[1])

  perfs.append(world.perf())
 print sum(perfs)/len(perfs)

 agent.learning=True
 ax.plot(x,y,'+')
 pl.draw()
  
if __name__=='__main__':
 world=mazerobot_world()
 actions=world.get_actions()
 agent=qagent(actions,lambda x:q_func_ann(x,isize=10,hsize=40),learn_online=False,do_static=True,replay=16)

 #agent=qagent(actions,q_func_lookup,learn_online=True)
 mx_time = 10000000

 reward=None
 terminal=False


 for step in xrange(mx_time):
  if step%50000==0:
   print step
   vis_rollout(agent,10,1000)

  obs=world.get_state()
  action = agent.act(obs,reward,terminal)
  reward,terminal = world.take_action(action)

 """
 a=mazepy.mazewrapper()
 a.load_env("hard_maze.txt")

 import pylab as pl
 from matplotlib import collections as mc

 segs=process_walls(a)
 lc = mc.LineCollection(segs)
 fig,ax = pl.subplots()
 ax.add_collection(lc)
 ax.autoscale()

 x=[]
 y=[]

 for ep in range(100):
  a.reset()
  for _ in xrange(600):
   behavior = a.get_behavior()
   x.append(behavior[0])
   y.append(behavior[1])
   a.take_action(random.randint(0,8))

 pl.plot(x,y,'+')
 pl.show()
 """
