import sys 
sys.setrecursionlimit(50000)

import copy
import numpy as np
import numpy
import random
import theano
import theano.tensor as T
import theano.tensor.nnet as nnet
from theano.printing import pydotprint
import mlp

#more sophisticated gradient descent training algorithm
def RMSprop(cost, params, lr=0.001, rho=0.9, epsilon=1e-6):
    grads = T.grad(cost=cost, wrt=params, disconnected_inputs='warn')
    updates = []
    for p, g in zip(params, grads):
        acc = theano.shared(numpy.array(p.get_value() * 0.,dtype=theano.config.floatX)) # acc is allocated for each parameter (p) with 0 values with the shape of p
        acc_new = rho * acc + (1 - rho) * g ** 2
        gradient_scaling = T.sqrt(acc_new + epsilon)
        g =  g / gradient_scaling
        g =  T.clip(g,-1,1)
        updates.append((acc, acc_new))
        updates.append((p, p - lr * g))
    return updates


world="""
       
       
      + 
       
      
           
"""

act_dx={'U':0,'D':0,'L':-1,'R':1}
act_dy={'U':-1,'D':1,'L':0,'R':0}


def parse_world(wrld):
 lines = wrld.split("\n")[1:-1]
 mx_sz=max(len(l) for l in lines)
 for k in range(len(lines)):
  lines[k]+=" "*(mx_sz-len(lines[k]))
 xdim=len(lines)
 ydim=mx_sz
 return xdim,ydim,lines


#simple grid world, reward for reaching goal
class gridworld:
 def __init__(self,wrld):
   self.episodes=-1
   self.episodeLength=0
   self.xdim,self.ydim,self.wrld = parse_world(wrld)
   self.reset()
 
 def get_actions(self):
  return ['U','L','R','D']

 def reset(self):
   found=False
   while found==False:
    x = random.randint(0,self.xdim-1)
    y = random.randint(0,self.ydim-1)
    if(self.wrld[x][y]==' '):
     self.px=x
     self.py=y
     found=True
   #self.px,self.py=0,0
   self.episodes+=1
   self.episodeLength=0

 def get_state(self):
   return (float(self.px)/self.xdim,float(self.py)/self.ydim)

 def vis(self):
   rep = np.zeros((self.xdim,self.ydim))

   for x in range(self.xdim):
    for y in range(self.ydim):
     block=self.wrld[x][y]
     if block=='x':
      rep[x,y]=-1
     elif block=='+':
      rep[x,y]=1
     elif block=='-':
      rep[x,y]=-0.5
   rep[self.px,self.py]=0.5
   return rep

 def v_mat(self,agent):
   rep = np.zeros((self.xdim,self.ydim))

   for x in range(self.xdim):
    for y in range(self.ydim):
     rep[x,y]=agent.v((float(x)/self.xdim,float(y)/self.ydim))
   return rep

 def a_mat(self,agent):
   dx=np.zeros((self.xdim,self.ydim))
   dy=np.zeros((self.xdim,self.ydim))

   for x in range(self.xdim):
    for y in range(self.ydim):
     state=(float(x)/self.xdim,float(y)/self.ydim)
     action=agent.max_action(state)
     dx[x,y]=act_dx[action]
     dy[x,y]=act_dy[action]
   return dx,dy

 def take_action(self,act):

   #if random.random()<0.1:
   # act=random.choice(act_dx.keys())

   dx = act_dx[act]
   dy = act_dy[act] 
   valid=True

   nx = self.px+dx
   ny = self.py+dy
 
   if nx<0 or nx>=self.xdim or ny<0 or ny>=self.ydim:
    valid=False
   else:
    if self.wrld[nx][ny]!='x':
     self.px=nx
     self.py=ny
   
   if self.wrld[self.px][self.py]=='+':
    self.reset()
    return 1.0,True
   elif self.wrld[self.px][self.py]=='-':
    self.reset()
    return -1.0,True  
   else:

    self.episodeLength+=1
    if self.episodeLength > 1000:
     print "too long.."
     self.reset()

    return -0.05,False

import collections

class random_agent:
 def __init__(self,acts):
  self.experiences=collections.deque(maxlen=100000)
  self.lastAct=None
  self.lastObs=None
  self.actions=acts

 def act(self,obs,rew=None,terminal=False):

  if self.lastAct!=None and rew!=None:
   #if rew==1.0 or random.random()<0.01:
   self.experiences.append((self.lastObs,self.lastAct,rew,obs,terminal))
  
  action=random.choice(self.actions)
 
  self.lastObs = obs
  self.lastAct = action

  if terminal:
   self.lastObs = None
   self.lastAct = None

  return action


class qagent:
 def __init__(self,acts,q_func=None,do_static=False,replay=0,learn_online=True):
  self.q_func=q_func(acts)

  self.experiences=collections.deque(maxlen=75000)
  self.results=collections.deque(maxlen=10000)

  self.actions=acts
  self.episodeLength=0
  self.explore=True
  self.lastAct=None
  self.lastObs=None
  self.alpha=0.05
  self.C=10000

  self.q_func.alpha=self.alpha
  self.q_static=self.q_func.makecopy()

  self.discount=0.98
  self.epsilon=1.0
  self.steps=0
  self.replay=replay
  self.learning=True
  self.static=do_static
  self.learn_online=learn_online
 
 def act(self,obs,rew=None,terminal=False):
  if self.static:
   q_learn=self.q_static
  else:
   q_learn=self.q_func

  self.steps+=1

  if self.static and self.steps%self.C==0:
   print "new q_static"
   self.q_static=self.q_func.makecopy()
   print self.epsilon,len(self.experiences)

  if self.steps%10000==0:
   self.epsilon=max(0.1,1.0-self.steps/100000.0)

  vals = [self.q_func.query((obs,k)) for k in self.actions]
  action = self.actions[np.argmax(vals)]

  if rew!=None and self.lastAct!=None:
   if self.learn_online and self.learning:
    self.learn([(self.lastObs,self.lastAct,rew,obs,terminal)],q_learn)

   #if rew==1.0 or random.random()<0.05:
   self.experiences.append((self.lastObs,self.lastAct,rew,obs,terminal))
  
   if self.learning: 
    if self.replay>0:
     self.learn(random.sample(self.experiences,self.replay),q_learn)

   self.results.append(rew) 
 
  if self.explore and random.random()<self.epsilon:
   action=random.choice(self.actions)
  
  self.lastObs = obs
  self.lastAct = action
 
  return action

 def max_action(self,state):
   vals=[self.q_func.query((state,k)) for k in self.actions]
   return self.actions[vals.index(max(vals))]

 def v(self,state):
   vals=[self.q_func.query((state,k)) for k in self.actions]
   return max(vals)

 def learn(self,experiences,ref_q):
  learning_tuples=[]
 
  for experience in experiences:
    lastObs,lastAct,rew,obs,terminal=experience

    q_old=self.q_func.query((lastObs,lastAct))
    q_new=rew

    if not terminal:
      #vals = [ref_q.query((obs,k)) for k in self.actions]
      #action = self.actions[np.argmax(vals)]
      action,val = ref_q.maxact(obs)
      q_new += self.discount*val
    learning_tuples.append(((lastObs,lastAct),q_old,q_new))

  self.q_func.learn(learning_tuples)
 
class q_func_lookup:

  def __init__(self,acts):
   self.q_table=collections.defaultdict(float)
   self.actions=acts

  def query(self,sa):
   return self.q_table[sa]

  def learn(self,tuples):
   for ex in tuples:
    sa,cur,target = ex
    self.q_table[sa]= (1.0-self.alpha) * cur + self.alpha*target

  def makecopy(self):
   ntable=q_func_lookup(self.actions)
   ntable.q_table=copy.deepcopy(self.q_table)
   return ntable

  def maxact(self,obs):
   vals = [self.query((obs,k)) for k in self.actions]
   action = self.actions[np.argmax(vals)]
   return action,max(vals) 

 
class q_func_ann:
  def __init__(self,acts,isize=2,hsize=40):
   self.costs=collections.deque(maxlen=2000)
   self.act_map={}
   self.ract_map={}
   self.isize=isize
   self.hsize=hsize

   cnt=0

   for k in acts:
    self.act_map[k]=cnt
    self.ract_map[cnt]=k
    cnt+=1

   rng = np.random.RandomState()
   self.inpvec = T.matrix('x')  # the data is presented as rasterized images
   self.inpvec_a = T.ivector('action')
   self.outvec = T.vector('y')  
   self.q_net=mlp.MLP(rng,self.inpvec,isize,hsize,len(acts))

   cost = self.q_net.squared_error(self.outvec,self.inpvec_a)
   updates = RMSprop(cost,self.q_net.params,lr=0.001)

   self.train=[]
   self.train_model = theano.function(
        inputs=[self.inpvec,self.inpvec_a,self.outvec],
        outputs=cost,
        updates=updates,
        #on_unused_input='warn'
    )

   self.run_net = theano.function(
	inputs=[self.inpvec],
        outputs=self.q_net.y,
        on_unused_input='warn'
    )

  def query(self,sa):
   action=None
   try:
    action=self.act_map[sa[1]]
   except:
    print sa
    afsd
   res= self.run_net(np.array([sa[0]],dtype=theano.config.floatX))
   return res[0,action]

  def maxval(self,s):
   res= self.run_net(np.array([s],dtype=theano.config.floatX))
   return res[0].max()

  def maxact(self,s):
   res= self.run_net(np.array([s],dtype=theano.config.floatX))
   return self.ract_map[np.argmax(res[0])],res[0].max()


  """
  def learn_from_scratch(self,tuples):
   states=numpy.zeros((len(tuples),2),dtype=theano.config.floatX)
   actions=numpy.zeros((len(tuples)),dtype=np.int32)
   targets=numpy.zeros((len(tuples)),dtype=theano.config.floatX)

   cnt=0 
   for ex in tuples:
     (sa,cur,target) = ex
     state=np.array([sa[0]],dtype=theano.config.floatX)
     action=np.array([self.act_map[sa[1]]],dtype=np.int32)
     target=np.array([target],dtype=theano.config.floatX)
 
     states[cnt,:]=state 
     actions[cnt]=action
     targets[cnt]=target
   for e in range(epochs):

   self.train_model(states,actions,targets)
  """

  def learn(self,tuples):
   states=numpy.zeros((len(tuples),self.isize),dtype=theano.config.floatX)
   actions=numpy.zeros((len(tuples)),dtype=np.int32)
   targets=numpy.zeros((len(tuples)),dtype=theano.config.floatX)

   cnt=0   
   for ex in tuples:
    (sa,cur,target) = ex
    state=sa[0]
    action=self.act_map[sa[1]]
    #target=np.array([target],dtype=theano.config.floatX)
 
    states[cnt,:]=state 
    actions[cnt]=action
    targets[cnt]=target
    cnt+=1
   
   cost =self.train_model(states,actions,targets)
   #print states,actions,targets
   ##print self.run_net(states)
   self.costs.append(cost) 
   return cost
   
  def makecopy(self):
   return copy.deepcopy(self) 

def process_experiences(exp):
 exps=[]
 for e in exp:
  lastObs,lastAct,rew,obs,terminal=e
  exps.append(((lastObs,lastAct),0,rew ))
 return exps

if(__name__=='__main__'):

 world=gridworld(world)
 actions=world.get_actions() 
 experience_gatherer=random_agent(actions)
 experiences=None
 reward=None
 terminal=False

 print "seeding experiences..."
 for k in range(75000):
  obs=world.get_state()
  action = experience_gatherer.act(obs,reward,terminal)
  reward,terminal = world.take_action(action)
 print "done.."

 do_ann=True
 agent=None

 if do_ann:
  neural_q = q_func_ann(actions)
  experiences=process_experiences(experience_gatherer.experiences)
  rsamp=random.sample(experiences,20)

  bah=np.random.random((10,2)) 
  neural_q.run_net(np.array(bah,dtype=theano.config.floatX))
  for k in range(10): 
   neural_q.run_net(np.array(bah[k:k+1,:],dtype=theano.config.floatX))

  #for k in range(30000):
  # rsamp=random.sample(experiences,16)
  # neural_q.learn(rsamp)
  # if k%1000==0:
  #  print sum(neural_q.costs)/len(neural_q.costs)

  agent=qagent(actions,q_func_ann,do_static=True,learn_online=False,replay=16)
  #agent.q_func=neural_q
 else:
  agent=qagent(actions,q_func_lookup)

 print len(experience_gatherer.experiences)
 agent.experiences=experience_gatherer.experiences

 mx_time = 1000000

 occupancy=np.zeros((world.xdim,world.ydim))
 import matplotlib
 matplotlib.use('tkagg')
 from pylab import *
 import copy
 import random
 ion()

 do_vis=False
 rewards=[]

 for step in xrange(mx_time):
  obs=world.get_state()
  occupancy[obs[0]*world.xdim,obs[1]*world.ydim]+=1
  action = agent.act(obs,reward,terminal)
  reward,terminal = world.take_action(action)

  if step>80001:
   do_vis=True
   agent.epsilon=0.01

  if do_vis and step%1==0:
   #print step
   #matshow(occupancy,fignum=0)
   #print np.unravel_index(np.argmax(occupancy),occupancy.shape)
   subplot()
   matshow(world.vis(),fignum=0)
   draw()
 
  if not do_vis and (step+1)%1000==0:
   if do_ann:
    print sum(agent.q_func.costs)/len(agent.q_func.costs)
 
   rewards.append(sum(agent.results)/len(agent.results))
   v_mat = world.v_mat(agent)
   #print v_mat.min(),v_mat.max()
   #print step,rewards[-1]
   #print step
   #matshow(occupancy,fignum=0)
   #print np.unravel_index(np.argmax(occupancy),occupancy.shape)
   figure(0,figsize=(12,12))
   clf()
   gray()
   subplot(511)
   dx,dy=world.a_mat(agent)
   quiver(dy,dx)
   subplot(512)
   matshow(v_mat,fignum=0)
   subplot(513)
   matshow(world.vis(),fignum=0)
   subplot(514)
   matshow(occupancy,fignum=0)
   subplot(515)
   plot(rewards)
   draw()
