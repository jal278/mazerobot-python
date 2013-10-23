#import pydot
#import svg_draw
import numpy
import sys
from sys import argv
import math
import os
import pygame
from pygame.time import Clock
from pygame.locals import *

def novelty(records,num,num2):
	tot_diff=0
	i1=records[num,11:91]
	i2=records[num2,11:91]
	for x in range(len(i1)):
		diff=i1[x]-i2[x]
		tot_diff+=diff*diff
	return tot_diff


def read_indiv(fn):
    ind_list =[]
    a=open(fn).read().split("\n")[:-1]
    for x in a:
        rest=x[x.find("Indiv:")+7:].split()[0]
        ind_list.append(int(rest))
    return ind_list

def read_pt(fn):
    pt_list=[]
    tot_point=[]
    a=open(fn).read().split("\n")[:-1]
    for x in a:
        rest=x.split()
	tot_pt=rest[2:-1]
	tot_pt=map(float,tot_pt)
	tot_point.append(tot_pt)
        pt=float(tot_pt[-2])*2,float(tot_pt[-1])*2
        pt_list.append(pt)

    return pt_list,tot_point

def readinrecord(fn):
    print fn
    a=open(fn).read().split("\n")[:-1]
    a=[[float(y) for y in x.split(" ")[:5]] for x in a]
    b=numpy.array(a)
    del a
    return b

#rec="../addedinfo_normthresh/m2b200n10record.dat" #sys.argv[2] 
#archive="../addedinfo_normthresh/m2b200n10rtarchive.dat"
#maze="maze2.txt" #sys.argv[1]
#rec=sys.argv[1] #"o/n1record.dat"

archive=sys.argv[1] #"no_novcrit_13rtarchive.dat"
maze="maze_explore2.txt"
if(len(sys.argv)>2):
   maze=sys.argv[2]

argc = len(sys.argv)
if(argc>1):
  archive=argv[1]
if(argc>2):
  maze=argv[2]

os.system("grep Novelty %s > nov_temp.dat" % archive)
os.system("grep Point %s > pt_temp.dat" % archive)

indiv_counter=read_indiv("nov_temp.dat")
indiv_coord,indiv_paths=read_pt("pt_temp.dat")

a=open(maze).read().split("\n")[:-1]

"""
b=readinrecord(rec)
b=numpy.hstack((numpy.reshape(numpy.arange(b.shape[0]),(b.shape[0],1)),b))
cutoff=b.shape[0]
"""
a=a[1:]
p1=map(int,a[1].split(" "))
p2=map(int,a[3].split(" "))
p3=map(int,a[4].split(" "))
lines=[map(int,x.split(" ")) for x in a[5:]]
scale = 1

pygame.init()
screen = pygame.display.set_mode((800, 600))
background = pygame.Surface(screen.get_size())
background = background.convert()



screen.blit(background, (0, 0))
pygame.display.flip()
clock=pygame.time.Clock()
counter=0
archive_counter=0
oldpt=None
oldpath=None

def rendpath(records,num,color=(255,0,0)):
	render_path(color,records[num,11:91],background,2)
	screen.blit(background,(0,0))
	pygame.display.flip()

def render_path(color,point,surface,scale):
	pts = []
	for x in range(len(point)/2):
		pts.append((point[2*x]*scale,point[2*x+1]*scale))
	pygame.draw.lines(surface,color,False,pts,1)

while 1:
    #while((counter+250)>indiv_counter[archive_counter]):
    background.fill((255, 255, 255))
    for x in lines:
        pygame.draw.line(background,(0,0,0),(x[0]*scale,x[1]*scale),(x[2]*scale,x[3]*scale),3)

    k=0
    pts = indiv_paths[counter]
    pygame.draw.line(background,(0,0,0),(p1[0]*scale,p1[1]*scale),
			(pts[0]*scale,pts[1]*scale),3)
    while(k<len(pts)):
       pygame.draw.circle(background,(k*5,k*5,k*2),(pts[k]*scale,pts[k+1]*scale),8,8)
       k+=2
       if (k<len(pts)):
           pygame.draw.line(background,(0,0,0),(pts[k-2]*scale,pts[k-1]*scale),
		(pts[k]*scale,pts[k+1]*scale),3)
    
    #    archive_counter+=1
    #clock.tick(5)
    #newpath=b[counter][11:91]
    #if(oldpath!=None):
    #    render_path((255,255,255),oldpath,background,2)
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            exit()
        elif event.type == KEYDOWN and event.key == K_RIGHT:
            counter+=1
            print counter
        elif event.type == KEYDOWN and event.key == K_UP:
            counter+=10
        elif event.type == KEYDOWN and event.key == K_LEFT:
            counter-=1
	    print counter
        if(counter>=len(indiv_paths)):
            counter = len(indiv_paths)-1
        if(counter<0):
            counter = len(indiv_paths)-1
	elif event.type == KEYDOWN and event.key == K_HOME:
            os.system("python extract.py %s %d" % (archive,counter))
    #if(counter%50==0):
    #    pygame.image.save(background,"outimages/out%04d.tga" % (counter/50))
    
    pygame.draw.circle(background,(0,0,255),(p1[0]*scale,p1[1]*scale),20,0)
    pygame.draw.circle(background,(0,255,0),(p2[0]*scale,p2[1]*scale),10,0)
    pygame.draw.circle(background,(255,0,0),(p3[0]*scale,p3[1]*scale),10,0)
    screen.blit(background,(0,0))
    pygame.display.flip()
