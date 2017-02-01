import PIL
from PIL import Image,ImageDraw
from pylab import *

def read_maze(fname='hard_maze.txt'):
 lines = open(fname).read().split("\n")[7:-1]
 coords = [[float(x) for x in line.split()] for line in lines]
 return coords

def transform_dim(c,rng_o,rng_n):
 interval = (c-rng_o[0])/(rng_o[1]-rng_o[0])
 return rng_n[0] + (rng_n[1]-rng_n[0])*interval

def transform_size(c,rng_o,rng_n):
 size_old = rng_o[1]-rng_o[0]
 size_new = rng_n[1]-rng_n[0]
 return (c/size_old)*size_new

def transform_pnt(c,xrng_o,yrng_o,xrng_n,yrng_n):
 return [transform_dim(c[0],xrng_o,xrng_n),transform_dim(c[1],yrng_o,yrng_n)]

def transform_line(line,xrng_old,yrng_old,xrng_new,yrng_new):
 return transform_pnt(line[0:2],xrng_old,yrng_old,xrng_new,yrng_new)+transform_pnt(line[2:],xrng_old,yrng_old,xrng_new,yrng_new)

def draw_maze(walls,agent=None,sz=64,fname=None):
 maze = Image.new('RGB',(sz,sz),(255,255,255))

 wallx = [c[0] for c in walls] + [c[2] for c in walls]
 wally = [c[1] for c in walls] + [c[3] for c in walls]

 buf = 5
 xrng = (min(wallx)-buf,max(wallx)+buf)
 yrng = (min(wally)-buf,max(wally)+buf) 
 
 d = ImageDraw.Draw(maze)
 for line in walls: 
  x0,y0,x1,y1 = transform_line(line,xrng,yrng,(0,sz-1),(0,sz-1))
  d.line([x0,y0,x1,y1],fill=(0,0,0),width=2)
 
 if agent!=None:
  hx,hy,heading = agent
  xprime,yprime = transform_pnt((hx,hy),xrng,yrng,(0,sz-1),(0,sz-1))
  radiusx = transform_size(8.0,xrng,(0,sz-1))
  radiusy = transform_size(8.0,yrng,(0,sz-1))
  heading_rad = (heading+180)/180.0 * 3.14

  xprime_head = xprime+math.cos(heading_rad)*radiusx
  yprime_head = yprime+math.sin(heading_rad)*radiusy

  d.ellipse([xprime-radiusx,yprime-radiusy,xprime+radiusx,yprime+radiusy],(255,0,0),(255,0,0))
 
  draw_heading=False
  if draw_heading:
   d.line([xprime,yprime,xprime_head,yprime_head],fill=(0,128,0),width=2)

 #if True:
 ## imshow(maze)
  show()

 if fname!=None:
  maze.save(fname) 

 return numpy.array(maze)

if __name__=='__main__':
 m = read_maze("../hard_maze.txt")
 draw_maze(m) 

