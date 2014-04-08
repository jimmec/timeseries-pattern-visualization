#!/bin/python2
import os
import sys
import numpy as np
import cPickle as pkl
from matplotlib.pyplot import figure, show
import matplotlib.gridspec as gridspec
from featuregenerator import preprocess as pp
from tsne import calc_tsne as tsne

def run(infile, pklpath, k, l, use_relative_err, max_error=float('inf')):
    if infile.name.endswith('.pkl'):
        print("Using previously computed data from " + infile.name)
        result, data, dates, segd, features, k, l = depickle_interm(infile)
    else:
        if k==None or l==None:
            print("Error: -k and -l must be specified if input file is not .pkl")
            return
        print("Generating features from Yahoo Finance CSV file " + infile.name)
        # extract features and segmented data from CSV file
        features, segd, dates, data = pp.gen_simple_features(infile, k, l, max_error)

        # convert to numpy 2-D array
        features = np.array(features)

        # run tsne
        tsneLocation = os.path.dirname(os.path.realpath(tsne.__file__)) + "/"
        result = tsne.calc_tsne(features, folderPrefix = tsneLocation)

        if pklpath != None:
            pickle_interm((result, data, dates, segd, features, k, l), pklpath)

    print("Generating plot")
    interactive_plot(result, segd, dates, data, k, l)

def pickle_interm(data, pklpath):
    # Format: data, dates, segd, features, k, l
    if not pklpath.endswith('.pkl'):
        pklpath = pklpath + '.pkl'

    outfile = open(pklpath, 'wb')
    pkl.dump(data, outfile)
    outfile.close()

def depickle_interm(pklfile):
    return pkl.load(pklfile)

def interactive_plot(result, segd, dates, data, seglength, windowlength):
    x,y = zip(*result)

    fig = figure(figsize=(8,10))

    gs = gridspec.GridSpec(2,1, height_ratios=[4,1])
    scatterplot = fig.add_subplot(gs[0])
    segmentplot = fig.add_subplot(gs[1])
    
    scatterplot.scatter(x, y, picker=True)
    scatterplot.set_title(
        'segment length: {}, window length:{}'.format(seglength,windowlength))

    # add a dot used to highlight the selected point
    dot = scatterplot.scatter(x[0],y[0])

    def onpick(event):
        # get segment to display
        ind = event.ind[0]
        seg = segd[ind: ind + windowlength]
        seg_inds, seg_vals = zip(*seg)
        seg_dates = [dates[i] for i in seg_inds]

        # highlight it
        dot.set_offsets((x[ind],y[ind]))
        dot.set_facecolors('r')

        # update plot
        segmentplot.clear()
        # plot the segment
        segmentplot.plot(seg_inds, seg_vals, 'r-')
        # plot the original un-segmented series
        segmentplot.plot(range(seg_inds[0], seg_inds[-1] + 1), 
            data[seg_inds[0]:(seg_inds[-1]+1)])

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
    aparser.add_argument('-in', 
        dest='inputFile', 
        default=sys.stdin,
        type=argparse.FileType('rb'),
        help='Path to .csv or .pkl file, reads from stdin if not specified')
    aparser.add_argument('-k', dest='segmentLength', 
        type=int,
        default=None,
        help='ALG. PARAM: Average length of segment')
    aparser.add_argument('-l', dest='windowLength', 
        type=int,
        default=None,
        help='ALG. PARAM: Length of sliding window')
    aparser.add_argument('-r', dest='use_relative_err',
        action='store_true',
        default=False,
        help='ALG. PARAM: Use relative residuals for segmentation')
    aparser.add_argument('-o', dest='storeLoc', 
        type=str,
        default=None,
        help='Optional location to store all intermediate data using Pickle')
    aparser.add_argument('-e', dest='maxerror', 
        type=float,
        default=float('inf'),
        help='Maximum allowed square residual during SEGMENTATION process')

    args = aparser.parse_args()

    try:
        run(args.inputFile, args.storeLoc, args.segmentLength, args.windowLength, args.maxerror)
    finally:
        args.inputFile.close()