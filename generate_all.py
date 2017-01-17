from multiprocessing import Pool
import os
import time
def do_job(x):
 start,number,output = x
 cmd = "./mazesim --ni %ld -p %ld -o %s" % (start,number,output)
 print "starting..."
 os.system(cmd) 
 print cmd 
 print "ending..."
 return 0

if __name__=='__main__':
 jobs = []
 index = 0
 offset = 0
 max_size = 200000
 total = 3**16

 while True:
  output = "logs/out%d.txt" % index
  remaining = total-index
  to_do = min(max_size,remaining)
  jobs.append((offset,to_do,output))
  
  offset+=to_do
  index+=1

  if offset>=total:
   break

 p = Pool(processes=6) 
 p.map(do_job,jobs)

