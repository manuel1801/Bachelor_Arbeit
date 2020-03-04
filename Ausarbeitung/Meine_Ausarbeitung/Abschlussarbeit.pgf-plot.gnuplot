set table "Abschlussarbeit.pgf-plot.table"; set format "%.5f"
set format "%.7e";; set samples 1001; set dummy x; plot [x=0:0.02] -log10(-0.5*(-0.01+x)/(0.1+x)+sqrt(0.25*((-0.01+x)/(0.1+x))**2+10**(-14)));
