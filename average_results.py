import glob
#c_win=18751
c_win=22500
m_win=9000
l_win=c_win

win=c_win
d="res-nospec"

f=glob.glob("%s/*_norm*log.txt"%d)
n=glob.glob("%s/*_alps*log.txt"%d)
n2=glob.glob("%s/*_pnov*log.txt"%d)



def read(k):
 f=k
 a=open(k).read().split("\n")[:-1]
 b=[float(k.split()[1]) for k in a]
 print f,len(b)
 return b

def max_arr(k):
 n=[]
 mx=0
 for z in k:
  mx=max(z,mx)
  n.append(mx)
 print len(n)
 return n[50:1000]

def true_arr(k):
 pad=1000
 n=[]
 mx=0
 for z in k:
  z=float(float(z/win))
  mx=max(z,mx)
  n.append(mx)
 #if len(n)<pad:
 # n+=[n[-1]]*(pad-len(n))
 return n[:pad]

def avg(k,sz=1000):
 k=[l[:sz] for l in k if len(l)>=sz]
 nm=len(k)
 c=len(k[0])
 print nm

 ret=[]
 for a in range(c):
  ret.append(sum([k[z][a] for z in range(nm)])/nm)
 return ret  
  
fit=[]
nov=[]
nov2=[]

fn=true_arr
#fn=max_arr
for k in f:
 fit.append(fn(read(k)))

for k in n:
 nov.append(fn(read(k)))

for k in n2:
 nov2.append(fn(read(k)))

fit_plot=avg(fit)
nov_plot=avg(nov)
nov2_plot=avg(nov2)

a=open("reactive.dat","w")
for k in range(1000):
 a.write("%d %f %f %f\n" % (k,fit_plot[k],nov_plot[k],nov2_plot[k]))
k=999
a.write("%d %f %f %f\n" % (k+1,fit_plot[k],nov_plot[k],nov2_plot[k]))
a.close()

from pylab import *
title("Learning results")
xlabel("Generations")
ylabel("Success Probability")
plot(avg(fit),'r-')
plot(avg(nov),'g-')
plot(avg(nov2),'k-')
legend( ('Fitness','Novelty (fine-grained)','Novelty (summary probabilities)'),loc='upper_left')

show()
