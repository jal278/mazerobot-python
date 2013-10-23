#ifndef GRAPH1010
#define GRAPH1010
#include <stdio.h>
#include <stdlib.h>
#include <vector>

using namespace std;
#define GRAPH_ENABLED false

class plot {
public:
    FILE *gp;
    bool enabled,persist;
    plot(bool _persist=false,bool _enabled=GRAPH_ENABLED) {
        enabled=_enabled;
        persist=_persist;
        if (enabled) {
            if(persist)
                gp=popen("gnuplot -persist","w");
            else
                gp=popen("gnuplot","w");
        }
    }

    void plot_data_2d(vector< vector<float> > rows, const char* style="points",const char*title="Data") {
        if(!enabled)
            return;
        fprintf(gp,"set title '%s' \n",title);
        fprintf(gp,"plot");
        for (int x=0; x<rows.size(); x++) {
            fprintf(gp,"'-' w %s",style);
            if(x<(rows.size()-1))
                fprintf(gp,",");
            else
                fprintf(gp,"\n");
        }

        for(int x=0; x<rows.size(); x++) {
            vector<float>& k=rows[x];

            for(int y=0; y<k.size(); y+=2) {
                fprintf(gp,"%f %f\n",k[y],k[y+1]);
            }
            fprintf(gp,"e\n");
        }
        fflush(gp);

    }


    void plot_data(vector< vector<float> > rows, const char* style="points",const char*title="Data") {
        if(!enabled)
            return;
        fprintf(gp,"set title '%s' \n",title);
        fprintf(gp,"plot");
        for (int x=0; x<rows.size(); x++) {
            fprintf(gp,"'-' w %s",style);
            if(x<(rows.size()-1))
                fprintf(gp,",");
            else
                fprintf(gp,"\n");
        }
        for(int x=0; x<rows.size(); x++) {
            vector<float>& k=rows[x];
            for(int y=0; y<k.size(); y++) {
                fprintf(gp,"%f\n",k[y]);
            }
            fprintf(gp,"e\n");
        }
        fflush(gp);


    }


    void plot_data(vector<float> x,const char* style="points",const char* title="Data") {
        if(!enabled)
            return;
        fprintf(gp,"set title '%s' \n",title);
        fprintf(gp,"plot '-' w %s \n",style);
        for(int k=0; k<x.size(); k++) {
            fprintf(gp,"%f\n",x[k]);
        }
        fprintf(gp,"e\n");
        fflush(gp);
    }

    void plot_data(vector<float> x,vector<float> y,const char* style="points",const char* title="Data") {
        if(!enabled)
            return;
        fprintf(gp,"set title '%s' \n",title);
        fprintf(gp,"plot '-' w %s \n",style);
        for(int k=0; k<x.size(); k++) {
            fprintf(gp,"%f %f \n",x[k],y[k]);
        }
        fprintf(gp,"e\n");
        fflush(gp);
    }

    ~plot() {
        if(enabled)
            pclose(gp);
    }

};

/*
int main(int argc,char **argv) {
 plot p;
 for(int a=0;a<100;a++) {
 vector<float> x,y;
 for(int k=a;k<a+200;k++) {
   x.push_back(k);
   y.push_back(k*k);
 }
  p.plot_data(x,y);
 }
 return 0;
}
*/

#endif
