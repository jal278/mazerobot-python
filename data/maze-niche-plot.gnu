set terminal png
set output "maze-niches.png"
set style data lines

set xlabel "Evaluations"
set ylabel "Occupied Niches"
set key bottom right
rows = "3 4"
plot for [i in rows] "maze-niches.dat" u 2:i w l title columnheader(i)

