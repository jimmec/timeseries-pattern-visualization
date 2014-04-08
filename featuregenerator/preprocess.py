#! /bin/python2
'''Time series preprocessing script
Author: JumboSliceKimboShrimp && Riceballicious

Preprocesses raw .csv format financial time series data using the Bottom-Up
segmenting algorithm and extracts features.

.csv import works with Yahoo Finance data. Remember to change the csv reader
properties when processing data from other sources!
'''
import sys
import csv
import segmenter
import featextract as fex

def csv_import(csvfile):
    # assume csv rows are in reverse chronological order
    # read csv into memory as a list of (INDEX,DATE,CLOSE_PRICE) tuples
    reader = csv.DictReader(csvfile)
    combined_data =  [(row['Date'], float(row['Close'])) for row in reader]

    # truncate odd length data
    if len(combined_data)%2 == 1:
        combined_data = combined_data[:-1]

    # extract dates and data into two separate lists
    dates, data = zip(*combined_data)

    # reverse order
    data = data[::-1]
    dates = dates[::-1]
    
    # enumerate it for the index
    return dates, data

def remove_consecutive_duplicates(segd):
    prev = float('nan')

    remove = []

    for i in xrange(len(segd)):
        s = segd[i]
        if s[1] == prev:
            remove.append(i)
        prev = s[1]

    for i in remove[::-1]:
        del segd[i] 

def gen_simple_features(inpath, outfile, k, l, 
    use_relative_err=False,
    max_error=float('inf')):
    # import Yahoo stock data and dates
    dates, data = csv_import(inpath)
    # segment data
    if use_relative_err:
        segd = segmenter.bottom_up(data, k,
            calc_error=segmenter.relative_sqr_residual, 
            max_error=max_error)
    else:
        segd = segmenter.bottom_up(data,k,max_error=max_error)
    # remove consecutive duplicates to eliminate 
    # possibility of division by zero
    remove_consecutive_duplicates(segd)
    # generate features 
    features = fex.extract_features(segd, l)

    if outfile != None:
        csv.writer(outfile, delimiter=',').writerows(features)

    return features, segd, dates

if __name__ == "__main__":
    import argparse

    aparser = argparse.ArgumentParser(description=
                'Preprocess time series from raw csv file')
    aparser.add_argument('-in',
        dest='csvFile', 
        default=sys.stdin,
        type=argparse.FileType('rb'),
        help='Path to .csv file, reads from stdin if not specified')
    aparser.add_argument(dest='segmentLength', 
        type=int,
        help='ALG. PARAM: Average length of segment')
    aparser.add_argument(dest='windowLength', 
        type=int,
        help='ALG. PARAM: Length of sliding window')
    aparser.add_argument('-o', dest='outputFile', 
        type=argparse.FileType('w'),
        default=None,
        help='Optional location to store extracted features as CSV')
    aparser.add_argument('-e', dest='maxerror', 
        type=float,
        default=float('inf'),
        help='Maximum allowed square residual during segmenting')

    args = aparser.parse_args()

    try:
        gen_features(args.csvFile, args.outputFile, args.segmentLength, args.windowLength, args.maxerror)
    finally:
        args.csvFile.close()
        if args.outputFile != None:
            args.outputFile.close()
