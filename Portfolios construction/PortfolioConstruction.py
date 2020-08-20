"""
File: PorftolioConstruction.py
Author: Daniel Stancl

utf-8
"""

# import libraries
import os
from os import listdir
from os.path import isfile, join

import numpy as np
import pandas as pd


# PortfolioConstruction class
class PorfolioConstruction(object):
    """
    The purpose of this class is to create decile long-short portfolios
    for individual months and for individual stock market indices.
    
    The output of this program is multiple of CSV files containing portfolio members
    over all months, separately for each index.

    At this moment, 
    """

    def __init__(self, company_path, bond_dataset, market_index='S&P 500'):
        self.stock_market_indices = ['S&P 500', 'FTSE 100', 'EURO STOXX 50']
        if market_index not in self.stock_market_indices:
            raise ValueError("Inappropriate arg value!")
        else:
            self.market_index = market_index

        all_companies = pd.read_csv(company_path, index_col=0)
        self.companies = {
            index: list(all_companies[all_companies.ListedOn == index].Company) for index in self.stock_market_indices
        }
        self.decile_size = {
            'S&P 500': 30,
            'FTSE 100': 1,
            'EURO STOXX 50': 1
        }

        self.bond_dataset = pd.read_csv(bond_dataset_path)
        # enforce date type
        self.bond_dataset['Date'] = pd.to_datetime(self.bond_dataset['Date'])

    def run(self, source_data_path, output_path, momentum, **kwargs):
        self._save_kwargs(kwargs)
        self.output_path = output_path
        datasets = self.load_datasets(source_data_path)

        self.experiment=0
        if momentum:
            self.create_portfolios(momentum=True)
        else:
            if self.use_ratings and self.use_shortterm:
                self.create_portfolios('Rating', '1M')
            if self.use_ratings and self.use_longterm:
                self.create_portfolios('Rating', '3M')
            if self.use_ratings and self.use_shortterm and self.use_diff:
                self.create_portfolios('Rating', '1M', use_diff=True)
            if self.use_ratings and self.use_longterm and self.use_diff:
                self.create_portfolios('Rating', '3M', use_diff=True)

    
    def create_portfolios(self, sentiment_base='', creation_period='', use_diff=False, momentum=False):
        self.experiment+=1
        if not momentum:
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
        elif momentum:
            try:
                # just pass auxiliry dataset to have date data
                sentiment_base, creation_period = 'Rating', '1M'
                data_name = [name for name in self.files if (sentiment_base in name) and (creation_period in name) and ('Diff' not in name)][0]
                data = self.datasets[data_name]
            except:
                raise FileNotFoundError(f'{data_name} does not exist.')

        # replace inf with nan, drop columns with NA
        data.replace(np.inf, np.nan, inplace=True)
        data.dropna(axis=1, how='all', inplace=True)

        LONGS, SHORTS = [],[]
        R_LONGS, R_SHORTS = [], []
        for date in data.columns:
            if not momentum:
                bonds_picked = self._create_single_portfolio(data, date)
            elif momentum:
                bonds_picked = self._create_single_momentum_portfolio(date)
            LONGS.append(bonds_picked['long'])
            SHORTS.append(bonds_picked['short'])
            
            # FINALLY - calculate return!! exciting again
            R_LONGS.append([self._calculate_return_on_bond(bond, 'long', date) for bond in bonds_picked['long']])
            R_SHORTS.append([self._calculate_return_on_bond(bond, 'short', date) for bond in bonds_picked['short']])
            print(f"Experiment no.{self.experiment} - Returns for {date} calculated.")
        
        # save created porfolios and returns for any future use
        if not momentum:
            [self.save_portfolio(portfolio, data.columns, pname, sentiment_base, creation_period, diff) for portfolio, pname in zip([LONGS, SHORTS], ['LONGS', 'SHORTS'])]
            [self.save_portfolio_returns(portfolio, data.columns, pname, sentiment_base, creation_period, diff) for portfolio, pname in zip([R_LONGS, R_SHORTS], ['LONGS', 'SHORTS'])]
        else:
            [self.save_momentum_portfolio(portfolio, data.columns, pname) for portfolio, pname in zip([LONGS, SHORTS], ['LONGS', 'SHORTS'])]
            [self.save_momentum_portfolio_returns(portfolio, data.columns, pname) for portfolio, pname in zip([R_LONGS, R_SHORTS], ['LONGS', 'SHORTS'])]

    def load_datasets(self, data_path):
        self.files = [f for f in listdir(data_path) if isfile(join(data_path, f))]
        self.datasets = {f: pd.read_csv(join(data_path, f), index_col=0) for f in self.files}
        return self.datasets
    
    def save_portfolio(self, portfolio, columns, portfolio_name, sentiment_base, creation_period, diff):
        portfolio_df = pd.DataFrame(portfolio).T
        portfolio_df.columns = columns
        fname = f"{portfolio_name}_{self.market_index}_{sentiment_base}_{creation_period}{diff}.csv"
        fpath = join(self.output_path, fname)
        portfolio_df.to_csv(fpath)
    
    def save_momentum_portfolio(self, portfolio, columns, portfolio_name):
        portfolio_df = pd.DataFrame(portfolio).T
        portfolio_df.columns = columns
        fname = f"{portfolio_name}_{self.market_index}_Momentum.csv"
        fpath = join(self.output_path, fname)
        portfolio_df.to_csv(fpath)
    
    def save_portfolio_returns(self, portfolio, columns, portfolio_name, sentiment_base, creation_period, diff):
        portfolio_df = pd.DataFrame(portfolio).T
        portfolio_df.columns = columns
        fname = f"RETURNS_{portfolio_name}_{self.market_index}_{sentiment_base}_{creation_period}{diff}.csv"
        fpath = join(self.output_path, fname)
        portfolio_df.to_csv(fpath)

    def save_momentum_portfolio_returns(self, portfolio, columns, portfolio_name):
        portfolio_df = pd.DataFrame(portfolio).T
        portfolio_df.columns = columns
        fname = f"RETURNS_{portfolio_name}_{self.market_index}_Momentum.csv"
        fpath = join(self.output_path, fname)
        portfolio_df.to_csv(fpath)

    def _calculate_return_on_bond(self, bond, long_short, date):
        year, month = [int(x) for x in date.split('-')][:2]
        if month != 12:
            year_t = year
            month_t = month + 1
        else:
            year_t = year + 1
            month_t=1
        # choose specific bond
        condition_1 = (self.bond_dataset.Date.apply(lambda x: x.year)==year) & (self.bond_dataset.Date.apply(lambda x: x.month)==month)
        condition_2 = (self.bond_dataset.Date.apply(lambda x: x.year)==year_t) & (self.bond_dataset.Date.apply(lambda x: x.month)==month_t)
        specific_bond = (
            self.bond_dataset[(condition_1 | condition_2) & (self.bond_dataset.Bond==bond)]
        )
        if long_short == 'long':
            try:
                buy_price = float(specific_bond[specific_bond.Date.apply(lambda x: x.month)==month]['Ask_price'])
                end_price = float(specific_bond[specific_bond.Date.apply(lambda x: x.month)==month_t]['Ask_price'])
                return np.round(
                    (end_price - buy_price) / end_price, 4
                )
            except:
                return 0

        elif long_short == 'short':
            try:
                sell_price = float(specific_bond[specific_bond.Date.apply(lambda x: x.month)==month]['Bid_price'])
                end_price = float(specific_bond[specific_bond.Date.apply(lambda x: x.month)==month_t]['Bid_price'])
                return np.round(
                    (sell_price - end_price) / sell_price, 4
                )
            except:
                return 0

    def _create_single_portfolio(self, data, date):
        # 1. extract year and month
        year, month = [int(x) for x in date.split('-')][:2]

        # 2. Extract considered companies from bond dataset
        actual_bonds = (
            self.bond_dataset[(self.bond_dataset.Date.apply(lambda x: x.year)==year) & (self.bond_dataset.Date.apply(lambda x: x.month)==month)]
        )

        # 3. Select companies to long/short
        data = (
            data[data.index.isin(actual_bonds.Company)]
            .loc[:, date]
            .dropna()
            .sort_values(ascending=False)
        )
        long_companies = list(data.index[:self.decile_size[self.market_index]])
        short_companies = list(data.index[-self.decile_size[self.market_index]:])

        # 4. Pick exact bonds to long/short
        BONDS_picked = {}
        for long_short, companies in zip(['long', 'short'], [long_companies, short_companies]):
            BONDS_picked[long_short] = [self._pick_bond(actual_bonds, company, long_short) for company in companies]
        return BONDS_picked
    
    def _create_single_momentum_portfolio(self, date):
        # 1. extract year, month and -3 months
        year, month = [int(x) for x in date.split('-')][:2]
        if month-3 >= 1:
            year_t = year
            month_t = month-3
        else:
            year_t = year-1
            month_t = month - 3 + 12

        # 2. Extract considered companies from bond dataset
        actual_bonds = (
            self.bond_dataset[(self.bond_dataset.Date.apply(lambda x: x.year)==year) & (self.bond_dataset.Date.apply(lambda x: x.month)==month)]
        )[['Bond', 'Date', 'Ask_price', 'Bid_price']]
        actual_bonds['Price'] = (actual_bonds['Ask_price'] + actual_bonds['Bid_price']) / 2

        # 3. Filter corresponding bonds and their records 3 months back
        actual_bonds_3M = self.bond_dataset[self.bond_dataset.Bond.isin(actual_bonds.Bond)]
        actual_bonds_3M = (
            actual_bonds_3M[(actual_bonds_3M.Date.apply(lambda x: x.year)==year_t) & (actual_bonds_3M.Date.apply(lambda x: x.month)==month_t)]
        )[['Bond', 'Date', 'Ask_price', 'Bid_price']]
        actual_bonds_3M.rename(columns={
            'Ask_price': 'Ask_price_t',
            'Bid_price': 'Bid_price_t'
        }, inplace=True)
        actual_bonds_3M['Price_t'] = (actual_bonds_3M['Ask_price_t'] + actual_bonds_3M['Bid_price_t']) / 2

        # 4. Calculate returns
        ## Drop date not to cramp join
        actual_bonds.drop('Date', axis=1, inplace=True), actual_bonds_3M.drop('Date', axis=1, inplace=True)
        
        bonds_join = (
            actual_bonds.set_index('Bond')
            .join(actual_bonds_3M.set_index('Bond'), on='Bond')
        )
        returns = (
            (bonds_join['Price'] - bonds_join['Price_t']) / bonds_join['Price_t']
        ).dropna().sort_values(ascending=False)

        # 5. Select companies to long and short
        BONDS_picked = {
            'long': list(returns.index[:self.decile_size[self.market_index]]),
            'short': list(returns.index[-self.decile_size[self.market_index]:])
        }
        return BONDS_picked

    def _pick_bond(self, actual_bonds, company, long_short):
        bonds = actual_bonds[actual_bonds.Company==company].sort_values('TTM')['Bond']
        idx = bonds.index
        if long_short == 'long':
            return bonds[idx[0]]
        elif long_short == 'short':
            return bonds[idx[-1]]

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
bond_dataset_path = '/mnt/c/Data/UCL/@MSc Project - Data and sources/List of bonds/Bond_EURO_dataset.csv'
source_data_path = '/mnt/c/Data/UCL/@MSc Project - Data and sources/Sentiment results/'
output_path = '/mnt/c/Data/UCL/@MSc Project - Data and sources/Sentiment results/Portfolios/'

kwargs = {
    'ratings': True,
    'reviews': True,
    'short_term': True,
    'long_term': True,
    'diff': True  
}


a=PorfolioConstruction(company_path, bond_dataset_path, 'EURO STOXX 50')
# run sentiment portfolio
a.run(source_data_path, output_path, False, **kwargs)
# run momentu portfolio
a.run(source_data_path, output_path, True, **kwargs)



