#ifndef _DATAREC_H_
#define _DATAREC_H_

#include <vector>
#include <fstream>
#include <iostream>
#include <stdio.h>

#define RECSIZE 10
using namespace std;
class logger
{
public:
    ofstream *ofile;
    logger(const char* fn) {
        ofile= new ofstream(fn);
    }

    ~logger() {
        ofile->close();
        delete ofile;
    }
};

class data_record
{
public:
    data_record(data_record& x) {
        for(int i=0; i<RECSIZE; i++)
            ToRec[i]=x.ToRec[i];
        indiv_number=x.indiv_number;
    }
    data_record()
    {
        for(int i=0; i<RECSIZE; i++)
            ToRec[i]=0.0;
        indiv_number=-1;
    }
    float ToRec[RECSIZE];
    int indiv_number;
};

class data_rec
{
public:
    vector<data_record*> data;

    void serialize(char*fn)
    {
        ofstream output(fn);
        if (!output) {
            perror ("The following error occurred");
            std::cerr<<"Can't open "<<fn<<" for output"<<std::endl;
            return;
        }

        for(int i=0; i<(int)data.size(); i++)
        {
            for(int j=0; j<RECSIZE; j++)
            {
                output << data[i]->ToRec[j] << " ";
            }
            output << data[i]->indiv_number << endl;
        }
        output.close();
    }

    void add_new(data_record* k)
    {
        data.push_back(k);
    }

    ~data_rec()
    {

    }
};

#endif
