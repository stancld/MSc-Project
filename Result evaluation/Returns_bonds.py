"""
File: Return_bonds.py
Author: Daniel Stancl

utf-8
"""
# import libraries
import os
from os import listdir
from os.path import isfile, join

import numpy as np
import pandas as pd

#################
### FUNCTIONS ###
#################


## data loader
def load_data(main_path, sentiment_base):
    """
    :param sentiment base: choose from 'review' or 'rating' or None
    :param main_path: path to the directory containing results

    :return datasets: dict of load datasets
    """
    if type(sentiment_base) not in [str, type(None)]:
        raise TypeError('Param sentiment_base must be a type of str.')
    if type(sentiment_base) != type(None):    
        if sentiment_base.capitalize() not in ['Rating', 'Review']:
            raise ValueError('Param sentiment_base must be either "rating" or "review" or None.')

    # load data
    files = [f for f in listdir(main_path) if isfile(join(main_path, f))]
    if type(sentiment_base) != type(None):
        files_selected = [f for f in files if (sentiment_base.capitalize() in f) and ('RETURNS' in f)]
    else:
        files_selected = [f for f in files if ('Momentum' in f) and ('RETURNS' in f)]
    datasets = {f: pd.read_csv(join(main_path, f), index_col=0) for f in files_selected}
    datasets_n = cut_data(datasets, sentiment_base)
    return datasets_n

def cut_data(datasets, sentiment_base):
    """
    Function which cut data so that all of them have the same dimensions

    :param dataset: dict of datasets obtained from load_data function

    :return cut_dataset: cut datasets with respect to the one with the fewest periods
    """
    min_dim = min(
        [dataset.shape[1] for dataset in datasets.values()]
    )
    if sentiment_base==None: # just to ensure we have same number of periods (not nice but needed)
        min_dim-=3
    
    return {key: dataset.iloc[:, -min_dim:] for (key, dataset) in datasets.items()}


def concatenate_longs_and_shorts(datasets):
    """
    :param datasets: datasets obtained from load_data function

    :return datasets_concatenated: datasets where LONG and SHORT portfolio returns are concatenated
    """
    data_keys = {
        strategy: [key for key in datasets.keys() if strategy in key] for strategy in ['LONGS', 'SHORTS'] 
    }
    [data_keys[strategy].sort() for strategy in data_keys.keys()]

    datasets_concatenated = {
        generate_key(long_key): datasets[long_key].append(datasets[short_key]) for (long_key, short_key) in zip(data_keys['LONGS'], data_keys['SHORTS'])
    }
    return datasets_concatenated    

def generate_key(long_key):
    """
    :param long_key: long_key of dictionary
    """
    return '_'.join([x for x in long_key.split('_') if x != 'LONGS'])

def compute_returns(data, key):
    """
    :param data: dataset obtained from concatenate_longs_and_shorts function
    :param key: key of a dictionary detemining names for output dictiony

    :return returns_dict: dictionary of dictionaries containing:
        - annualized return
        - mean return
        - standard dev.
        - t-statistics (absolute value)
    """
    month_returns = data.mean(axis=0)
    return {
        'Mean return': np.round(100*month_returns.mean(), 4),
        'St. dev.': np.round(100*month_returns.std(), 4),
        '|t|': np.round(
            np.abs(
                month_returns.mean() / (month_returns.std() / np.sqrt(month_returns.shape[0]))
            ), 2
        ),
        'Annualized return': np.round(100*((1+month_returns.mean())**12 - 1), 4),
        'T': data.shape[1]
    }