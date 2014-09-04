set terminal png
set output "maze-mean.png"
set style data lines

set xlabel "Evaluations"
set ylabel "Average Evolvability"
set key bottom right
plot for [i=3:6] "maze-mean.dat" u 2:i w l title columnheader(i)

