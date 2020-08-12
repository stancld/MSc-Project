# import libraries
import os
from os import listdir
from os.path import isfile, join

import numpy as np
import pandas as pd



class PorfolioConstruction(object):
    """
    The purpose of this class is to create decile long-short portfolios
    for individual months and for individual stock market indices.
    
    The output of this program is multiple of CSV files containing portfolio members
    over all months, separately for each index.

    At this moment, 
    """

    def __init__(self, company_path):
        self.stock_market_indices = ['S&P 500', 'FTSE 100', 'EURO STOXX 50']
        all_companies = pd.read_csv(company_path, index_col=0)
        self.companies = {
            index: list(all_companies[all_companies.ListedOn == index].Company) for index in self.stock_market_indices
        }
        self.decile_size = {
            index: len(self.companies[index]) // 10 for index in self.stock_market_indices
        }
        
    def run(self, source_data_path, output_path, **kwargs):
        self._save_kwargs(kwargs)
        self.output_path = output_path
        datasets = self.load_datasets(source_data_path)

        if self.use_ratings and self.use_shortterm:
            self.create_portfolios('Rating', '1M')
        if self.use_ratings and self.use_longterm:
            self.create_portfolios('Rating', '3M')
        if self.use_ratings and self.use_shortterm and self.use_diff:
            self.create_portfolios('Rating', '1M', use_diff=True)
        if self.use_ratings and self.use_longterm and self.use_diff:
            self.create_portfolios('Rating', '3M', use_diff=True)


    
    def create_portfolios(self, sentiment_base, creation_period, use_diff=False):
        try:
            if use_diff==False:
                data_name = [name for name in self.files if (sentiment_base in name) and (creation_period in name) and ('Diff' not in name)][0]
                diff=''
            else:
                data_name = [name for name in self.files if (sentiment_base in name) and (creation_period in name) and ('Diff' in name)][0]
                diff='_Diff'
            data = self.datasets[data_name]
        except:
            raise FileNotFoundError(f'{data_name} does not exist.')

        # replace inf with nan, drop columns with NA
        data.replace(np.inf, np.nan, inplace=True)
        data.dropna(axis=1, how='all', inplace=True)
        for stock_index in self.stock_market_indices:
            LONGS, SHORTS = [],[]
            for month in data.columns:
                longs, shorts = self._create_single_portfolio(data, stock_index, month)
                LONGS.append(longs)
                SHORTS.append(shorts)
            self.L, self.S = LONGS, SHORTS
            [self.save_portfolio(portfolio, data.columns, pname, stock_index, sentiment_base, creation_period, diff) for portfolio, pname in zip([LONGS, SHORTS], ['LONGS', 'SHROTS'])]
    
    def load_datasets(self, data_path):
        self.files = [f for f in listdir(data_path) if isfile(join(data_path, f))]
        self.datasets = {f: pd.read_csv(join(data_path, f), index_col=0) for f in self.files}
        return self.datasets
    
    def save_portfolio(self, portfolio, columns, portfolio_name, stock_index, sentiment_base, creation_period, diff):
        portfolio_df = pd.DataFrame(portfolio).T
        portfolio_df.columns = columns
        fname = f"{portfolio_name}_{stock_index}_{sentiment_base}_{creation_period}{diff}.csv"
        fpath = join(self.output_path, fname)
        portfolio_df.to_csv(fpath)

    def _create_single_portfolio(self, data, stock_index, month):
        data = (
            data[data.index.isin(self.companies[stock_index])]
            .loc[:, month]
            .dropna()
            .sort_values(ascending=False)
        )
        longs = list(data.index[:self.decile_size[stock_index]])
        shorts = list(data.index[-self.decile_size[stock_index]:])
        return longs, shorts

    def _save_kwargs(self, kwargs):
        self.use_ratings = (True if kwargs['ratings']==True else False)
        self.use_reviews = (True if kwargs['reviews']==True else False)
        self.use_shortterm = (True if kwargs['short_term']==True else False)
        self.use_longterm = (True if kwargs['long_term']==True else False)
        self.use_diff = (True if kwargs['diff']==True else False)


##########
## TEST ##
##########
company_path = '/mnt/c/Data/UCL/@MSc Project - Data and sources/Sentiment results/companies_filtered.csv'
source_data_path = '/mnt/c/Data/UCL/@MSc Project - Data and sources/Sentiment results/'
output_path = '/mnt/c/Data/UCL/@MSc Project - Data and sources/Sentiment results/Portfolios/'

kwargs = {
    'ratings': True,
    'reviews': True,
    'short_term': True,
    'long_term': True,
    'diff': True
}


a=PorfolioConstruction(company_path)
a.run(source_data_path, output_path, **kwargs)

