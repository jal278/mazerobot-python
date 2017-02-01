#!/usr/bin/env python
"""
An animated image
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from read_domain import precomputed_maze_domain,search

fig = plt.figure()

def make_image(
def f(x, y):
    return np.sin(x) + np.cos(y)

x = np.linspace(0, 2 * np.pi, 120)
y = np.linspace(0, 2 * np.pi, 100).reshape(-1, 1)

im = plt.imshow(f(x, y), cmap=plt.get_cmap('summer'), animated=True)


def updatefig(*args):
    global x, y
    x += np.pi / 15.
    y += np.pi / 20.
    im.set_array(f(x, y))
    return im,


img = np.zeros((sz,sz,4))

if __name__=='__main__':
 domain = precomputed_maze_domain()
 search = search(domain)
 img = 
ani = animation.FuncAnimation(fig, updatefig, interval=50, blit=True)
plt.show()
