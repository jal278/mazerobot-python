'''
Created on 10/01/2011

@author: 04610922479
'''
import random, math
from nsga2.nsga2 import Solution
from nsga2.nsga2 import NSGAII

#from nsga2.nsga2 import Solution

import mazepy
import numpy
from entropy import *

NOV=1
FIT=0
CUR=2

obj=[NOV,CUR]

mazepy.mazenav.initmaze("hard_maze_list.txt")
mazepy.mazenav.random_seed()

class MazeSolution(Solution):
    '''
    Solution for the T1 function.
    '''
    def __init__(self,robot=False):
        '''
        Constructor.
        '''
        Solution.__init__(self, len(obj))
        self.objs=[0.0]*3
        if(not robot):
         self.robot=mazepy.mazenav()
         self.robot.init_rand()
         self.robot.mutate()
        else:
         self.robot=robot
    def evaluate_solution(self):
        '''
        Implementation of method evaluate_solution() for T1 function.
        '''
        self.robot.map()
        if(self.robot.solution()):
         print "solution"
        self.objs[FIT] = mazepy.feature_detector.end_goal(self.robot)
        self.objs[CUR] = -mazepy.feature_detector.state_entropy(self.robot)
        self.behavior=numpy.array([mazepy.feature_detector.endx(self.robot),mazepy.feature_detector.endy(self.robot)])

    def evaluate2(self,pop):
        self.dists=[sum((self.behavior-x.behavior)**2) for x in pop]
        self.dists.sort()
        self.objs[NOV] = -sum(self.dists[:15])
        for k in range(len(obj)):
         self.objectives[k]=self.objs[obj[k]]

    def crossover(self, other):
        '''
        Crossover of T1 solutions.
        '''
        child_solution = MazeSolution(self.robot.copy())
        
        return child_solution
    
    def mutate(self):
        '''
        Mutation of T1 solution.
        '''
        self.robot.mutate()
    
if __name__ == '__main__':

    nsga2 = NSGAII(len(obj), 0.9, 1.0)
    
    P = []
    for i in range(250):
        P.append(MazeSolution())
    
    nsga2.run(P, 250, 251)
    csv_file = open('/tmp/nsga2_out.csv', 'w')
    
    for i in range(len(P)):
        csv_file.write("" + str(P[i].objectives[0]) + ", " + str(P[i].objectives[1]) + "\n")
        
    csv_file.close()
