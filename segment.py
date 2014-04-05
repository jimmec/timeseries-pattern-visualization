#! /bin/python
'''Time series segmenting script
Author: JumboSliceKimboShrimp && Riceballicious

Preprocesses raw .csv format financial time series data using the Bottom-Up
segmenting algorithm.

.csv import works with Yahoo Finance data. Remember to change the csv reader
properties when processing data from other sources!
'''

import csv
import math
import llist

def parse_csv(filepath):
    # assume csv rows are in chronological order
    # read csv into memory as a list of (INDEX,DATE,CLOSE_PRICE) tuples
    with open(filepath, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        data =  [float(row['Adj Close']) for row in reader]

    # truncate odd length data
    if len(data)%2 == 1:
        data = data[:-1]

    # reverse order
    data = data[::-1]
    
    # enumerate it for the index
    return data

def sqr_residual(segment, data):
    '''
    Input is a segment of the form
    ((index1, value1), (index2, value2))
    where index2 > index1 corresponds to indices in the data
    '''

    # change in value per change in index
    m = (segment[1][1] - segment[0][1]) / (segment[1][0] - segment[0][0])

    # number of intermediate points
    n = segment[1][0] - segment[0][0]

    pred = [segment[0][1] + m*i for i in range(1,n)]
    value = [data[segment[0][0] + i] for i in range(1,n)]
    sqr_residual = [(pred[i] - value[i])**2 for i in range(n-1)]

    return sum(sqr_residual)

def merge_segs(seg1, seg2, data):
    new_seg = (seg1[0], seg2[1])
    res = sqr_residual(new_seg)

    return (new_seg, r)

def bottom_up(data, k, max_error=0):
    '''
    Merge time series data points to produce trend segments
    using bottom-up method where k is the average segment length.
    '''

    n = len(data)

    # split into segments of length 2
    # data is now ((index, value), (index, value))
    segments = [((2*i,data[2*i]), (2*i+1,data[2*i+1])) for i in range(n/2)]

    residuals = llist.dlist()

    for i in range(len(segments)-1)