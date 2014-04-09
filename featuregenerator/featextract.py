'''Time series feature extractor
Author: JumboSliceKimboShrimp & Riceballicious

Given a segmented time series as a list of (index,value) pairs of 
length N, and a constant L<N,
extract fixed length L windows of the segmented time series and output a 
set of L+1 features for each window. 

Each window is a pair (p_start,p_end).
Each feature set is a tuple (f0,f1,...,fL)

E.g. input: list of segments [p0,p1,p2,...,pN]
     output: [(f00,f01,...,f0L), (f10,f11,...,f1L),...
                ,(fk0,fk1,...,fkL))], k=N-L+1

'''

import numpy as np

def compute_simple_trend_features(window):
    '''Given a window of N points as a list, 
    compute N+1 trend features as described
    in http://www.cs.ucsb.edu/~nanli/publications/stock_pattern.pdf
    and returns a list of N+1 features 
    '''

    # generate features 
    midfeats = [(window[i]-window[i-1])/(window[i-1]-window[i-2]) 
        for i in xrange(2,len(window))]
    feats = [np.sign(window[1]-window[0])]
    feats.extend(midfeats)
    feats.append((window[-1]-window[1])/abs(window[2]-window[1])) 

    return feats

def compute_jimmy_and_ricky_simple_trend_features(window):

    # generate features 
    midfeats = [(window[i]-window[i-2])/(window[i-1]-window[i-2]) 
        for i in xrange(2,len(window))]
    feats = [window[-1]-window[0]]
    feats.extend(midfeats)
    feats.append((window[-1]-window[1])/abs(window[2]-window[1])) 

    return feats

def compute_jimmy_and_ricky_acf_features(window):
    length = len(window)-2
    acf = [np.corrcoef(window[:-i], window[i:])[1,0] for i in xrange(1, length)]

    first = [window[-1] - window[0]]

    return first + acf

def extract_features(data, l, 
                    compute_feature=compute_jimmy_and_ricky_acf_features):
    '''Given data as a list of (index,value) pairs,
    and 1<l<len(data),
    extracts features for sliding windows of width length l
    using the routine compute_feature
    '''
    if l >= len(data) or l < 1:
        raise Exception(
            ('Invalid window length=',l, ' with segmented data length=',len(data)))

    garbage, vals = zip(*data)

    features = [compute_feature(vals[i:i+l]) 
        for i in xrange(len(vals)-l+1)]

    return standardize(features)

def standardize(features):
    # standardizes every feature to standard normal
    # while preserving distribution
    mean = np.mean(features, 0)
    std = np.std(features, 0)

    return (features - mean) / std

def classify(segd, l):
    inds, vals = zip(*segd)
    segs = [vals[i:i+l] for i in xrange(len(vals)-l+1)]

    classes = [0] * len(segs)

    for i in xrange(len(segs)):
        s = segs[i]

        inc = s[-1] - s[0]
        top = max(s)
        bot = min(s)
        revTOP = top > s[-1] and top > s[0]
        revBOT = bot < s[-1] and bot < s[0]
        if revTOP and revBOT:
            # wavey pattern?
            continue
        elif revTOP:
            # reversal pattern INC-DEC
            classes[i] = 1
            continue
        elif revBOT:
            # reversal pattern DEC-INC
            classes[i] = 2
            continue
        elif inc > 0:
            # continuation pattern INC
            classes[i] = 3
        elif inc < 0:
            # continuation pattern DEC
            classes[i] = 4

    return classes