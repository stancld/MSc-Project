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
    default='/mnt/c/Data/UCL/@MSc Project - Data and sources/Sentiment results/Portfolios/Reviews'
)

parser.add_argument(
    '--sentiment_base', help="choose from 'reviews' or 'rating' or None",
    default=''
)

parser.add_argument(
    '--multi_factor', help="specify base for mutli-factor model",
    default=''
)

parser.add_argument(
    '--multi_factor_full', help='Indication if whole single portfolios to be used for multi-factor one',
    action='store_true'
)

parser.add_argument(
    '--concatenate', help='Indication if long-short returns to be computed',
    action='store_true'
)

args = parser.parse_args()

###################
### APPLICATION ###
###################
def main():
    datasets = load_data(args.main_path, args.sentiment_base, args.multi_factor, args.multi_factor_full)
    returns = {
        key: compute_returns(data, key) for (key, data) in datasets.items() 
    }
    if args.sentiment_base=='':
        args.sentiment_base = args.multi_factor
        if args.multi_factor_full:
            args.sentiment_base += '_full'
    pd.DataFrame(returns).to_excel(join(args.main_path, f'results_{args.sentiment_base}.xlsx'))
    
    if args.concatenate:
        datasets_concatenated = concatenate_longs_and_shorts(datasets)
        returns_concatenated = {
            key: compute_returns(data, key) for (key, data) in datasets_concatenated.items() 
        }
        if args.sentiment_base=='':
            args.sentiment_base = args.multi_factor
            if args.multi_factor_full:
                args.sentiment_base += 'full'
        pd.DataFrame(returns_concatenated).to_excel(join(args.main_path, f'results_concat_{args.sentiment_base}.xlsx'))

if __name__=='__main__':
    main()