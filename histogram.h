/* Created by Anjuta version 1.2.4a */
/*	This file will not be overwritten */
#ifndef HISTOGRAM
#define HISTOGRAM

#include <iostream>
#include <fstream>
#include <vector>
#include <cstdlib>
#include <math.h>

#define realtype float

using namespace std;

//Function for creating a normalized histogram of an input vector given a number of bins
//not currently used
void pdf(vector<realtype> &input, vector<realtype> &bins, vector<realtype> &hist,bool clear=true);

void window_filter(vector<realtype> &input, int winsize, vector<realtype> &res);

//multiresolution histogram, not used currently
void multires_hist(vector<realtype> &input, vector<realtype> &bins, vector<int> &granularities, vector<realtype> &res);

void write_vect(char *fn,vector<realtype> res);

//calculates item-wise difference between two vectors
realtype hist_diff(vector<realtype> &in1, vector<realtype> &in2);

//test routines
void hist_test();
#endif
