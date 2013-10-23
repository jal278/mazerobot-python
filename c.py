import glob
import os

f=glob.glob("*record.dat")
k=[]
for x in f:
   print x
   os.system("cat %s | wc > temp.dat" % x)
   z=float(open("temp.dat").read().split()[0])
   print z
   k.append(z)
print k
print sum(k)/len(k)
