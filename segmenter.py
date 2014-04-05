#! /bin/python
'''Time series segmenting script
Author: JumboSliceKimboShrimp

Preprocesses raw .csv format financial time series data using the Bottom-Up
segmenting algorithm.

.csv import works with Yahoo Finance data. Remember to change the csv reader
properties when processing data from other sources!
'''
import csv
import itertools
import math
import heapdict


def parse_csv(filepath):
    # read csv into memory as a list of (INDEX,DATE,CLOSE_PRICE) tuples
    with open(filepath, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        data =  [(row['Date'],float(row['Adj Close'])) for row in reader]

    # truncate odd length data
    if len(data)%2 == 1:
        data = data[:-1]
    
    # reverse the list, so that oldest date is at data[0]
    data = data[::-1]
    # enumerate it for the index
    return [(index,d,p) for index,(d,p) in enumerate(data)]

def create_segment(ts_chunk):
    '''Turns the input ts into a segment by simply returning a tuple 
    with the first and last point in the list ts_chunk.
    '''
    return (ts_chunk[0],ts_chunk[-1])

def pairwise(iterable):
    '''s -> (s0,s1), (s1,s2), (s2, s3), ...'''
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)

def grouper(iterable, n, fillvalue=None):
    '''Collect data into fixed-length chunks or blocks
    grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    '''
    args = [iter(iterable)] * n
    return itertools.izip_longest(fillvalue=fillvalue, *args)


def calculate_error(seg,data):
    '''
    Given a segment, calculate the residual error with the original data
    Input: seg - a segment tuple ((INDEX,DATE,PRICE),(INDEX2,DATE2,PRICE2))
           data -  original data
    Returns the RMSE
    '''
    # get parameterization of interpolated line segment y=mx+b
    m = (seg[1][2]-seg[0][2])/(seg[1][0]-seg[0][0])
    b = seg[0][2]-m*seg[0][0]
    n = seg[1][0]-seg[0][0]+1
    
    # calculate residual sum squared error
    for i in range(seg[0][0],seg[1][0]+1):
        err += (m*i+b - data[i][2])**2

    return math.sqrt(err)/n



def bottom_up(ts_data, avg_seg_length, max_error=0):
    '''
    Merge time series data points to produce trend segments.
    
    Given time series data in ts_data as a list of tuples (date,price),
    uses Bottom-Up segmenting to produce a time series with segments of 
    average length avg_seg_length.
    
    OR 
    
    if max_error > 0, segments will be merged until the maximum error of any 
    segment (in terms of a residual with the original data underlying the 
    segment) has reached the limit.
    
    A segment is just a pair of points from the original time series
    ((date0,p0),(date1,p1)), the start and the end of the segment.
    '''
    # do the initial round of merging each 2i-1 and 2i points
    merged = [create_segment(p) for p in grouper(ts_data,2)]

    # calculate errors for each neighbouring segments
    errors = [(calculate_errors(create_segment([p0,p1])),p0) for 
                (p0,p1) in pairwise(merged)]

    # heapify the list
    heapq.heapify(errors)
    
    return None


if __name__ == "__main__":
    import argparse
    aparser = argparse.ArgumentParser(description=
                'Segment time series from raw csv file')
    aparser.add_argument(dest='csvpath', help='path to .csv file')

    args = aparser.parse_args()
    
    # parse the csv file specified on commandline
    data = parse_csv(args.csvpath)

   
