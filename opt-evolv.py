
from entropy import *
if(__name__=='__main__'):
 evo_fnc = calc_evolvability_entropy
 #initialize maze stuff with "medium maze" 
 mazepy.mazenav.initmaze("hard_maze_list.txt")
 #mazepy.mazenav.initmaze("medium_maze_list.txt")
 mazepy.mazenav.random_seed()

 robot=None

 population=defaultdict(list)
 whole_population=[]
 psize=15
 e_samp=100

 for k in range(psize):
  robot=mazepy.mazenav()
  robot.init_rand()
  robot.mutate()
  robot.map()
  robot.fitness=evo_fnc(robot,e_samp)
  whole_population.append(robot)

 solved=False

 evals=psize
 child=None
 while not solved:
  evals+=1

  parent=random.choice(whole_population)
  parent.fitness=evo_fnc(robot,e_samp)
  child=parent.copy()
  child.mutate()
  child.map()
  child.fitness=evo_fnc(robot,e_samp)

  if(child.solution()):
   solved=True

  whole_population.append(child)
  whole_population.sort(key=lambda k:k.fitness,reverse=True)

  to_kill=whole_population[-1]
  #print to_kill.fitness
  whole_population.remove(to_kill)
  del to_kill

  if(evals%25==0):
   print evals,calc_population_entropy(whole_population),whole_population[0].fitness,whole_population[-1].fitness
 #run genome in the maze simulator

 #calculate evolvability
 print child.solution()
 print "evolvability:", evo_fnc(child,1000)

 robot=mazepy.mazenav()
 robot.init_rand()
 robot.mutate()
 robot.map()
 print "evolvability:", evo_fnc(robot,1000)
