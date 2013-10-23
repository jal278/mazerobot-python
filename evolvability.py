import mazepy

def map_into_grid(robot,grid_sz):
 x=mazepy.feature_detector.endx(robot)
 y=mazepy.feature_detector.endy(robot)
 x_grid=int(x*(grid_sz-1))
 y_grid=int(x*(grid_sz-1))
 return (x_grid,y_grid)

def calc_evolvability(robot,grid_sz,mutations):
 grids=set()
 for x in range(mutations):
  mutant=robot.copy()
  mutant.mutate()
  mutant.map()
  grids.add(map_into_grid(mutant,grid_sz))
 return len(grids)

if(__name__=='__main__'):
 #initialize maze stuff with "medium maze" 
 mazepy.mazenav.initmaze("hard_maze_list.txt")
 mazepy.mazenav.random_seed()

 #create initial genome
 robot=mazepy.mazenav()


 #initalize it randomly and mutate it once for good measure
 robot.init_rand()
 robot.mutate()

 #run genome in the maze simulator
 robot.map()

 #calculate evolvability
 print "evolvability:", calc_evolvability(robot,30,200)
