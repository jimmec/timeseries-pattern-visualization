#!/bin/python2
import matplotlib.dates as mdates
from matplotlib.pyplot import figure, show, subplots
from featuregenerator import preprocess as pp
from featuregenerator import segmenter as sgt

def run(infile, k, max_error=float('inf')):
    # extract features and segmented data from CSV file
    dates, data = pp.csv_import(infile)
    segd1 = sgt.bottom_up(data,k,calc_error=sgt.sqr_residual)
    segd2 = sgt.bottom_up(data,k,calc_error=sgt.relative_sqr_residual)

    # convert dates to matplotlib.dates
    dates = map(mdates.strpdate2num('%Y-%m-%d'),dates)

    # plot segmented time series versus original
    fig, (orig_ts, seg1_ts, seg2_ts) = subplots(3, sharex=True)
    fig.set_size_inches(8,10)

    orig_ts.plot_date(dates,data,'b-')
    orig_ts.set_title('original data')
    seg_inds1, seg_vals1 = zip(*segd1)
    seg_dates1 = [dates[i] for i in seg_inds1]
    seg_inds2, seg_vals2 = zip(*segd2)
    seg_dates2 = [dates[i] for i in seg_inds2]
    seg1_ts.plot_date(seg_dates1, seg_vals1, 'r-')
    seg1_ts.set_title('abs. residual error segmenting')
    seg2_ts.plot_date(seg_dates2, seg_vals2, 'g-')
    seg2_ts.set_title('rel. residual error segmenting')

    # auto space the dates x-ticks
    fig.autofmt_xdate()
    show()


if __name__ == '__main__':
    import argparse

    aparser = argparse.ArgumentParser(description=
                '''Compare financial time series segmentation,
                reads csv from Yahoo Finance''')
    aparser.add_argument('-in', 
        dest='csvFile', 
        default=sys.stdin,
        type=argparse.FileType('rb'),
        help='Path to .csv file, reads from stdin if not specified')
    aparser.add_argument(dest='segmentLength', 
        type=int,
        help='ALG. PARAM: Average length of segment')
    aparser.add_argument('-e', dest='maxerror', 
        type=float,
        default=float('inf'),
        help='Maximum allowed square residual during SEGMENTATION process')

    args = aparser.parse_args()

    try:
        run(args.csvFile, args.segmentLength, args.maxerror)
    finally:
        args.csvFile.close()
        if args.outputFile != None:
            args.outputFile.close()
