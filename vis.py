#import pydot
import svg_draw
import numpy
import sys
import math
import os

def readinrecord(fn):
    print fn
    a=open(fn).read().split("\n")[:-1]
    a=[[float(y) for y in x.split(" ")] for x in a]
    b=numpy.array(a)
    return b

def dist(x1,y1,x2,y2):
    xd=x1-x2
    yd=y1-y2
    return math.sqrt(xd*xd+yd*yd)

a=open(sys.argv[1]).read().split("\n")[3:-1]
if(len(sys.argv)==3):
    b=readinrecord(sys.argv[2])
else:
    b=numpy.array([])

cutoff=0
if(len(sys.argv)>3):
    b=readinrecord(sys.argv[2])
    b=numpy.hstack((numpy.reshape(numpy.arange(b.shape[0]),(b.shape[0],1)),b))
    cutoff=b.shape[0]
else:
    cutoff=(-1)
    for x in range(b.shape[0]):
        if(b[x,3]>0):
            cutoff=x
            break

    if(cutoff==-1):
        cutoff=b.shape[0]
    else:
        cutoff+=1

p1=map(int,a[1].split(" "))
p2=map(int,a[3].split(" "))
p3=map(int,a[4].split(" "))

lines=[map(int,x.split(" ")) for x in a[5:]]

print p1,p2,p3

scene = svg_draw.Scene("test",width=450,height=550)
scale = 2.0


for x in lines:
    scene.add(svg_draw.Line((x[0]*scale,x[1]*scale),(x[2]*scale,x[3]*scale),(0,0,0)))

#scene.add(svg_draw.Circle((p2[0]*scale,p2[1]*scale),5,(255,255,255),False))
#scene.add(svg_draw.Circle((p3[0]*scale,p3[1]*scale),3,(255,255,255),False))
scene.add(svg_draw.Text((p2[0]*scale,p2[1]*scale),"B",24))
scene.add(svg_draw.Text((p3[0]*scale,p3[1]*scale),"S",20))

#cutoff=b.shape[0]
for x in range(cutoff):
    color = 0
    #color = 200-(float(x)/cutoff)*200
    #color = dist(b[x,1],b[x,2],p2[0],p2[1])/300.0*200+75
    if(color>255):
        color=255
    scene.add(svg_draw.Circle((int(b[x,1]*scale),int(b[x,2]*scale)),2,(0,0,255),False))

scene.add(svg_draw.Circle((p1[0]*scale,p1[1]*scale),10,(255,255,255),False))


scene.write_svg()
scene.display()

#g=pydot.graph_from_edges(lines,directed=True)
#e.write("blah.txt")
#e.write_jpeg('graph.jpg',prog='fdp')

