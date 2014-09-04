set terminal png
set output "maze-max.png"
set style data lines

set xlabel "Evaluations"
set ylabel "Maximum Evolvability"
set key bottom right
plot for [i=3:6] "maze-max.dat" u 2:i w l title columnheader(i)

