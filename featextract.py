#! /bin/python
'''Time series feature extractor
Author: JumboSliceKimboShrimp

Given a segmented time series as a list of (index,value) pairs of 
length N+1, and a constant L<N+1,
extract fixed length L+1 windows of the segmented time series and output a 
set of L+1 features for each window. 

Each window is a pair (p_start,p_end).
Each feature set is a tuple (f0,f1,...,fL)

E.g. input: list of segments [p0,p1,p2,...,pN]
     output: [((p0,pL),(f0,f1,...,fL)), ((p1,pL+1),(f0,f1,...,fL)),...
                ,((pN-L,pN),(f0,f1,...,fL))]

'''
import itertools

def compute_simple_trend_features(window):
    '''Given a window of N points, compute N+1 trend features as described
    in http://www.cs.ucsb.edu/~nanli/publications/stock_pattern.pdf
    '''
    midfeats = [(window[i]-window[i-1])/(window[i-1]-window[i-2]) 
        for i in xrange(2,len(window))]
    feats = [(window[1]-window[0])/abs(window[1]-window[0])]
        .extend(midfeats)
        .append((window[-1]-window[1])/abs(window[2]-window[1]))

    return tuple(feats)

    
def extract_features(data, length, compute_feature):
    '''Given data as a list of (index,value) pairs,
    and length<len(data),
    extracts features for sliding windows of width length
    '''
    return [((data[i],data[i+n]),compute_feature(data[i:i+n])) 
        for i in xrange(len(data)-n+1)]
    

