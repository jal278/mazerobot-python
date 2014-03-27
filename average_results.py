import glob
c_win=18751
#c_win=22500
m_win=9000
l_win=c_win
ofn="reactive.dat"
#ofn="success.dat"

win=c_win
d="res_hard"

f=glob.glob("%s-nospec/*_norm*log.txt"%d)
fhm=glob.glob("%s-nospec/*_hinorm*log.txt"%d)
fs=glob.glob("%s/*_norm*log.txt"%d)
a=glob.glob("%s-nospec/*_falps*log.txt"%d)
n=glob.glob("%s-nospec/*_pnov*log.txt"%d)



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
  z=float(int(z/win))
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
fithm=[]
fits=[]
alps=[]
nov=[]

fn=true_arr
#fn=max_arr
for k in f:
 fit.append(fn(read(k)))

for k in fs:
 fits.append(fn(read(k)))

for k in fhm:
 fithm.append(fn(read(k)))

for k in n:
 nov.append(fn(read(k)))

for k in a:
 alps.append(fn(read(k)))

fit_plot=avg(fit)
fits_plot=avg(fits)
fithm_plot=avg(fithm)
nov_plot=avg(nov)
alps_plot=avg(alps)

a=open(ofn,"w")
for k in range(1000):
 a.write("%d %f %f %f %f %f\n" % (k,fit_plot[k],fits_plot[k],fithm_plot[k],nov_plot[k],alps_plot[k]))
k=999
a.write("%d %f %f %f %f %f\n" % (k+1,fit_plot[k],fits_plot[k],fithm_plot[k],nov_plot[k],alps_plot[k]))
a.close()

from pylab import *
title("Learning results")
xlabel("Generations")
ylabel("Success Probability")
plot(avg(fit),'r-')
plot(avg(fits),'g-')
plot(avg(nov),'k-')
plot(avg(alps),'b-')
plot(avg(fithm),'y-')
legend( ('Fitness','FItS','Nov','alps','himut'),loc='upper_left')

show()
