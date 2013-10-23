import sys

fname=sys.argv[1] #"archive.dat"
num=int(sys.argv[2]) #20
a=open(fname).read()
a=a.split("/* Novelty")

out="temp2.dat"
out=open(out,"w")
if num==0:
   out.write(a[0])
else:
   towrite=a[num]
   print a[num+1].split("\n")[0]
   f=towrite.find("*/")
   f=towrite.find("*/",f+1)
   out.write(towrite[f+3:])
out.close()

import os
os.system('grep -v \* temp2.dat > mazebrain.dat') 
os.system("./maze")
#os.system("gnuplot plotstuff.gnu -persist")
