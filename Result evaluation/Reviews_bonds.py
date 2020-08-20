import os
from os import listdir
from os.path import isfile, join

import numpy as np
import pandas as pd

#################
### FUNCTIONS ###
#################


## data loader
def load_data(sentiment_base, main_path='/mnt/c/Data/UCL/@MSc Project - Data and sources/Sentiment results/Portfolios'):
    """
    :param sentiment base: choose from 'review' or 'rating'
    :param main_path: path to the directory containing results
        default: '/mnt/c/Data/UCL/@MSc Project - Data and sources/Sentiment results/Porfolios'

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
    return datasets

def concatenate_longs_and_shorts(datasets):
    """
    :param datasets: datasets obtained from load_data function

    :return datasets: datasets where LONG and SHORT portfolio returns are concatenated
    """

def compute_returns(data, key):
    """
    :param data: dataset obtained from concatenate_longs_and_shorts function
    :param key: key of a dictionary detemining names for output dictiony

    :return returns_dict: dictionary of dictionaries containing:
        - mean return
        - standard dev.
        - t-statistics
    """
    month_returns = data.mean(axis=0)
    return {
        'mean': np.round(100*month_returns.mean(), 4),
        'std': np.round(100*month_returns.std(), 4),
        't-value': month_returns.mean() / month_returns.std()
    }



###########
### RUN ###
###########

datasets = load_data('rating')
returns = {
    key: compute_returns(data, key) for (key, data) in datasets.items() 
}

for data in returns.keys():
    print(data+':', returns[data])
