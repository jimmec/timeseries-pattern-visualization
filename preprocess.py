#! /bin/python
'''Time series preprocessing script
Author: JumboSliceKimboShrimp

Preprocesses raw .csv format financial time series data using the Bottom-Up
segmenting algorithm and extracts features.

.csv import works with Yahoo Finance data. Remember to change the csv reader
properties when processing data from other sources!
'''
import sys
import csv
import itertools
import math



def parse_csv(filepath):
    # assume csv rows are in chronological order
    # read csv into memory as a list of (INDEX,DATE,CLOSE_PRICE) tuples
    with open(filepath, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        combined_data =  [(row['Date'], float(row['Adj Close'])) for row in reader]

    # truncate odd length data
    if len(combined_data)%2 == 1:
        combined_data = combined_data[:-1]

    # extract dates and data into two separate lists
    dates, data = zip(*combined_data)

    # reverse order
    data = data[::-1]
    
    # enumerate it for the index
    return dates, data

if __name__ == "__main__":
    import argparse
    aparser = argparse.ArgumentParser(description=
                'Preprocess time series from raw csv file')
    aparser.add_argument(dest='csvpath', help='path to .csv file')
    aparser.add_argument(dest='slength', help='average length of segment')
    aparser.add_argument(dest='wlength', help='length of sliding window')
    aparser.add_argument(dest='outfile', nargs='?', 
        type=argparse.FileType('w'),
        default=sys.stdout)

    args = aparser.parse_args()
    
    # parse the csv file specified on commandline
    data = parse_csv(args.csvpath)

   
