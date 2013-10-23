import subprocess
import glob

def get_evol(fn):
   proc = subprocess.Popen("./a.out %s" % fn,
			shell=True,
			stdout=subprocess.PIPE,)
   print fn + "...."
   stdout = [x for x in proc.communicate()[0].split("\n")[:-1]]
   return float(stdout[1]),float(stdout[0])

#nov_temp = "novgen%d__evolvability%d.dat"
#fit_temp = "fitgen%d__evolvability%d.dat"

#nov_pts = []
#fit_pts = []
files=glob.glob("*evolvability*.dat")
a=open("evolvability.txt","w")
for x in files:
 y=get_evol(x)
 line= x + " " + str(y[0]) + " " + str(y[1])
 print line
 a.write(line+"\n")
