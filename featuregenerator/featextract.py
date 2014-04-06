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

def compute_simple_trend_features(window):
    '''Given a window of N points as a list, 
    compute N+1 trend features as described
    in http://www.cs.ucsb.edu/~nanli/publications/stock_pattern.pdf
    and returns a list of N+1 features 
    '''

    # generate features 
    midfeats = [(window[i][1]-window[i-1][1])/(window[i-1][1]-window[i-2][1]) 
        for i in xrange(2,len(window))]
    feats = [(window[1][1]-window[0][1])/abs(window[1][1]-window[0][1])]
    feats.extend(midfeats)
    feats.append((window[-1][1]-window[1][1])/abs(window[2][1]-window[1][1]))

    return feats
    
def extract_features(data, l, 
                    compute_feature=compute_simple_trend_features):
    '''Given data as a list of (index,value) pairs,
    and 1<l<len(data),
    extracts features for sliding windows of width length l
    using the routine compute_feature
    '''
    if l >= len(data) or l < 1:
        raise Exception(
            ('Invalid window length=',l, ' with segmented data length=',len(data)))

    return [compute_feature(data[i:i+l]) 
        for i in xrange(len(data)-l+1)]