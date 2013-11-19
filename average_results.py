import glob

f=glob.glob("comm*norm*log.txt")
n=glob.glob("comm*nov*log.txt")

def read(k):
 a=open(k).read().split("\n")[:-1]
 b=[float(k.split()[1]) for k in a]
 return b

def max_arr(k):
 n=[]
 mx=0
 for z in k:
  mx=max(z,mx)
  n.append(mx)
 return n[0:500]

def true_arr(k):
 n=[]
 mx=0
 for z in k:
  z=float(int(z/5000.0))
  mx=max(z,mx)
  n.append(mx)
 return n[0:1000]

def avg(k):
 nm=len(k)
 c=len(k[0])

 ret=[]
 for a in range(c):
  ret.append(sum([k[z][a] for z in range(nm)])/nm)
 return ret  
  
fit=[]
nov=[]

fn=true_arr
for k in f:
 fit.append(fn(read(k)))
 print fit[-1] 
for k in n:
 nov.append(fn(read(k)))

from pylab import *
plot(avg(fit),'r+')
plot(avg(nov),'g+')
show()
