mazerobot-python
================

Python wrapper for the maze navigation evolutionary robotics domain common across many of my publications.

The program is built using SCons (http://www.scons.org/)

Building the program should (ideally) be as simple as executing scons in the working directory (only tested on Linux but should work ok on Windows if necessary).

To run the maze navigation experiment from the evolvability paper:

./mazesim -m hard_maze_list.txt --passive -o [output directory]

There is also a visualizer to see what the maze looks like and how a particular genome solves the maze (you can build it with makeVisualizer.sh) it requires installing wxWidgets to build though.

test.py showcases the python interface.

Dependencies:

python2 developer libraries and includes (to build python wrapper)
wxWidgets developer libraries and includes (to build visualizer)

