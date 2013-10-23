#import pydot
import svg_draw
import numpy
import sys
import math
import os

skip = 1
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

a=open(sys.argv[1]).read().split("\n")[skip:-1]
if(len(sys.argv)==3):
    b=readinrecord(sys.argv[2])
else:
    b=numpy.array([])

cutoff=2000
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
linearr=zip(*lines)

border=10
minx=min(linearr[0]+linearr[2])-border
miny=min(linearr[1]+linearr[3])-border
maxx=max(linearr[0]+linearr[2])+border
maxy=max(linearr[1]+linearr[3])+border

class Scaler:
 def __init__(self,mins,maxs,dims):
  self.mins=mins
  self.maxs=maxs
  self.dims=dims
  self.sz=len(mins)
 def scale(self,pt):
  res=[]
  for k in range(self.sz):
   res.append(int(float(pt[k]-self.mins[k])/(self.maxs[k]-self.mins[k])*self.dims[k]))
  return res

width=450
height=450

scaler=Scaler((minx,miny),(maxx,maxy),(width,height))


scene = svg_draw.Scene("test",width=450,height=450)


for x in lines:
    scene.add(svg_draw.Line(scaler.scale(x[0:2]),scaler.scale(x[2:4]),(0,0,0)))

scene.add(svg_draw.Circle(map(lambda x:x,scaler.scale(p2)),7,(0,0,0),True))
scene.add(svg_draw.Circle(map(lambda x:x,scaler.scale(p3)),4,(0,0,0),True))


cutoff=b.shape[0]
for x in range(cutoff):
    color = 0
    #color = 200-(float(x)/cutoff)*200
    #color = dist(b[x,1],b[x,2],p2[0],p2[1])/300.0*200+75
    if(color>255):
        color=255
    scene.add(svg_draw.Circle(scaler.scale((b[x,1],b[x,2])),2,(0,0,255),False))


scene.add(svg_draw.Circle(scaler.scale(p1),10,(255,255,255),False))

#scene.add(svg_draw.Rectangle(scaler.scale(p1),20,20,(255,255,255)))

scene.write_svg()
scene.display()

#g=pydot.graph_from_edges(lines,directed=True)
#e.write("blah.txt")
#e.write_jpeg('graph.jpg',prog='fdp')

