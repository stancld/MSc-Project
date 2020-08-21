"""
File: Return_bonds_main.py
Author: Daniel Stancl

utf-8
"""
# import libraries
from argparse import ArgumentParser
import os
from os import listdir
from os.path import isfile, join

import numpy as np
import pandas as pd

from Returns_bonds import load_data, concatenate_longs_and_shorts, generate_key, compute_returns

## load argument
parser = ArgumentParser()

parser.add_argument(
    '--main_path', help='path to the directory containing results',
    default='/mnt/c/Data/UCL/@MSc Project - Data and sources/Sentiment results/Portfolios/New'
)

parser.add_argument(
    '--sentiment_base', help="choose from 'review' or 'rating' or None"
)

args = parser.parse_args()

###################
### APPLICATION ###
###################
def main():
    datasets = load_data(args.main_path, args.sentiment_base)
    datasets_concatenated = concatenate_longs_and_shorts(datasets)

    returns = {
        key: compute_returns(data, key) for (key, data) in datasets.items() 
    }

    returns_concatenated = {
        key: compute_returns(data, key) for (key, data) in datasets_concatenated.items() 
    }
    # save results
    if args.sentiment_base == None:
        args.sentiment_base='momentum'
    pd.DataFrame(returns).to_excel(join(args.main_path, f'results_{args.sentiment_base}.xlsx'))
    pd.DataFrame(returns_concatenated).to_excel(join(args.main_path, f'results_concat_{args.sentiment_base}.xlsx'))

if __name__=='__main__':
    main()