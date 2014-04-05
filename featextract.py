#! /bin/python
'''Time series feature extractor
Author: JumboSliceKimboShrimp

Given a segmented time series as a list of (index,value) pairs of 
length N+1, and a constant L<N+1,
extract fixed length L+1 windows of the segmented time series and output a 
set of L+1 features for each window. 

Each window is a pair (p_start,p_end).
Each feature set is a tuple (f0,f1,...,fL)

E.g. input: list of segments [p0,p1,p2,...,pN]
     output: [((p0,pL),(f0,f1,...,fL)), ((p1,pL+1),(f0,f1,...,fL)),...
                ,((pN-L,pN),(f0,f1,...,fL))]

'''


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


if __name__ == "__main__":
    import argparse
    aparser = argparse.ArgumentParser(description=
                'Extract features from a time series')
    aparser.add_argument(dest='csvpath', help='path to .csv file')

    args = aparser.parse_args()
    
    # parse the csv file specified on commandline
    data = parse_csv(args.csvpath)

   
