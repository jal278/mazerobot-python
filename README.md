mazerobot-python
================

Python wrapper for the maze navigation evolutionary robotics domain common across many of my publications.

The program is built using SCons (http://www.scons.org/)

Building
--------

Before you build, the following dependencies should be installed:
* python2.x developer libraries and includes (to build python wrapper)
* wxWidgets developer libraries and includes (to build visualizer)


After these dependencies are installed, building the program should (ideally) be as simple as executing scons in the working directory (note: only tested on Linux but I don't believe anything is linux-specific).

Quick-start
-----------

To run the maze navigation experiment from "Evolvability is Inevitable":

    mazesim -m hard_maze_list.txt --passive -o [output directory]

There is also a visualizer to see what the maze looks like and how a particular genome solves the maze (which can be built through makeVisualizer.sh). Note that the visualizer depends upon wxWidgets to build though. Running the visualizer takes the following format:

    maze <mazefile> <brainfile>

test\_neuroevolution.py showcases the python interface
