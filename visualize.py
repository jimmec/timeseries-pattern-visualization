#!/bin/python2
import os
import numpy as np
from matplotlib.pyplot import figure, show
import matplotlib.gridspec as gridspec
from featuregenerator import preprocess as pp
from tsne import calc_tsne as tsne

def run(infile, outfile, k, l, max_error=float('inf')):
    # extract features and segmented data from CSV file
    features, segd, dates = pp.gen_simple_features(infile, outfile, k, l, max_error)

    # convert to numpy 2-D array
    features = np.array(features)

    # run tsne
    tsneLocation = os.path.dirname(os.path.realpath(tsne.__file__)) + "/"
    result = tsne.calc_tsne(features, folderPrefix = tsneLocation)

    interactive_plot(result, segd, dates, l)

def interactive_plot(result, segd, dates, windowlength):
    x,y = zip(*result)

    fig = figure(figsize=(8,10))

    gs = gridspec.GridSpec(2,1, height_ratios=[4,1])
    scatterplot = fig.add_subplot(gs[0])
    segmentplot = fig.add_subplot(gs[1])
    
    scatterplot.scatter(x, y, picker=True)

    def onpick(event):
        # get segment to display
        ind = event.ind[0]
        seg = segd[ind: ind + windowlength]
        seg_inds, seg_vals = zip(*seg)
        seg_dates = [dates[i] for i in seg_inds]

        # update plot
        segmentplot.clear()
        segmentplot.plot(seg_inds, seg_vals, 'r-')
        # update with correct dates
        tickinds = segmentplot.xaxis.get_majorticklocs()
        tickdates = [dates[int(tickinds[0])]] + ['']*(len(tickinds)-2) + [dates[int(tickinds[-1])]]
        segmentplot.set_xticklabels(tickdates)
        segmentplot.set_yticklabels([])

        fig.canvas.draw()

    #fig.savefig('')
    fig.canvas.mpl_connect('pick_event', onpick)
    show()

if __name__ == '__main__':
    import argparse

    aparser = argparse.ArgumentParser(description=
                'Visualize stock segments extracted from Yahoo Finance')
    aparser.add_argument(dest='csvFile', 
        type=argparse.FileType('rb'),
        help='Path to .csv file')
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
        help='Maximum allowed square residual during SEGMENTATION process')

    args = aparser.parse_args()

    try:
        run(args.csvFile, args.outputFile, args.segmentLength, args.windowLength, args.maxerror)
    finally:
        args.csvFile.close()
        if args.outputFile != None:
            args.outputFile.close()