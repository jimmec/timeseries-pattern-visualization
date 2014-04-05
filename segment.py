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
import heapdict as hd

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

    pred = [segment[0][1] + m*i for i in xrange(1,n)]
    value = [data[segment[0][0] + i] for i in xrange(1,n)]
    sqr_residual = [(pred[i] - value[i])**2 for i in xrange(n-1)]

    return sum(sqr_residual)

def merge_segs(seg1, seg2):
    return (seg1[0], seg2[1])

def bottom_up(data, k, max_error=0):
    '''
    Merge time series data points to produce trend segments
    using bottom-up method where k is the average segment length.
    '''

    ## INITIALIZATION STEP
    n = len(data)

    # split into segments of length 2
    # a segment is of the form ((index, value), (index, value))
    segments = [((2*i,data[2*i]), (2*i+1,data[2*i+1])) for i in xrange(n/2)]

    # create linked list of pairs of segments
    # and a heap dictionary of (pair -> sqr_residual) 
    pairs = llist.dllist()
    res_heap = hd.heapdict()

    for i in xrange(len(segments)-1):
        # create the pair
        left = segments[i]
        right = segments[i+1]
        seg_pair = (left, right)
        
        # get the squared residual
        res = sqr_residual(merge_segs(left, right), data)

        # add to linked list and heap
        node = pairs.append(seg_pair)
        res_heap[node] = res

    ## MERGE STEP
    # merge segments while number of segments at most n/k
    while len(pairs) > n/k:
        pair = res_heap.popitem()[0]

        new_seg = merge_segs(pair.value[0], pair.value[1])

        # update second segment of left pair in linked list and also
        # delete old left pair from heap and re-add new pair with new res
        left = pair.prev
        if left != None:
            del res_heap[left]
            lpair = left.value
            left.value = (lpair[0], new_seg)
            merged = merge_segs(left.value[0], left.value[1])
            res_heap[left] = sqr_residual(merged, data)

        # update first segment of right pair
        right = pair.next
        if right != None:
            del res_heap[right]
            rpair = right.value
            right.value = (new_seg, rpair[1])
            merged = merge_segs(right.value[0], right.value[1])
            res_heap[right] = sqr_residual(merged, data)

        # remove old pair from pairs linked list
        pairs.remove(pair)


    # form a list of (index, value) keeping 
    # only the values after being segmented
    segmented_data = []

    # retrieve unique segments
    head = pairs.first
    while head != None:
        unique_seg = head.value[0]
        segmented_data.append(unique_seg[0])
        segmented_data.append(unique_seg[1])
        head = head.next

    # add the last data point
    segmented_data.append(pairs.last.value[1][1])

    return segmented_data