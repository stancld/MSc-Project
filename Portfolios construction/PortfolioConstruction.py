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
class PortfolioConstruction(object):
    """
    The purpose of this class is to create decile long-short portfolios
    for individual months and for individual stock market indices.
    
    The output of this program is multiple of CSV files containing portfolio members
    over all months, separately for each index.

    At this moment, 
    """

    def __init__(self, company_path, bond_dataset_path, market_index='S&P 500'):
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

    def run(self, source_data_path, output_path, momentum, low_risk, **kwargs):
        self._save_kwargs(kwargs)
        self.output_path = output_path
        datasets = self.load_datasets(source_data_path)

        self.experiment=0
        if momentum:
            self.create_portfolios(momentum=True)
        elif low_risk:
            self.create_portfolios(low_risk=True)
        else:
            if not self.weighted:
                if self.use_ratings and self.use_shortterm:
                    self.create_portfolios('Rating', '1M')
                if self.use_ratings and self.use_longterm:
                    self.create_portfolios('Rating', '3M')
                if self.use_ratings and self.use_shortterm and self.use_diff:
                    self.create_portfolios('Rating', '1M', use_diff=True)
                if self.use_ratings and self.use_longterm and self.use_diff:
                    self.create_portfolios('Rating', '3M', use_diff=True)
                if self.use_reviews and self.use_shortterm:
                    self.create_portfolios('Reviews', '1M')
                if self.use_reviews and self.use_longterm:
                    self.create_portfolios('Reviews', '3M')
                if self.use_reviews and self.use_shortterm and self.use_diff:
                    self.create_portfolios('Reviews', '1M', use_diff=True)
                if self.use_reviews and self.use_longterm and self.use_diff:
                    self.create_portfolios('Reviews', '3M', use_diff=True)
            
            elif self.weighted:
                #if self.use_reviews and self.use_shortterm:
                #    self.create_portfolios('Reviews', '1M', weighted=True)
                #if self.use_reviews and self.use_longterm:
                #    self.create_portfolios('Reviews', '3M', weighted=True)
                #if self.use_reviews and self.use_shortterm and self.use_diff:
                #    self.create_portfolios('Reviews', '1M', use_diff=True, weighted=True)
                if self.use_reviews and self.use_longterm and self.use_diff:
                    self.create_portfolios('Reviews', '3M', use_diff=True, weighted=True)


    
    def create_portfolios(self, sentiment_base='', creation_period='', use_diff=False, weighted=False, momentum=False, low_risk=False):
        self.experiment+=1
        if momentum or low_risk:
            try:
                # just pass auxiliry dataset to have date data
                sentiment_base, creation_period = 'Rating', '1M'
                data_name = [name for name in self.files if (sentiment_base in name) and (creation_period in name) and ('Diff' not in name)][0]
                data = self.datasets[data_name]
            except:
                raise FileNotFoundError('File does not exist')
        
        else:
            try:
                if use_diff==False:
                    if not weighted:
                        data_name = [name for name in self.files if (sentiment_base in name) and (creation_period in name) and ('Diff' not in name) and ('Weighted' not in name)][0]
                        w_name=''
                    else:
                        data_name = [name for name in self.files if (sentiment_base in name) and (creation_period in name) and ('Diff' not in name) and ('Weighted' in name)][0]
                        w_name = 'Weighted'
                    diff=''
                else:
                    if not weighted:
                        data_name = [name for name in self.files if (sentiment_base in name) and (creation_period in name) and ('Diff' in name) and ('Weighted' not in name)][0]
                        w_name = ''
                    else:
                        data_name = [name for name in self.files if (sentiment_base in name) and (creation_period in name) and ('Diff' in name) and ('Weighted' in name)][0]
                        w_name = 'Weighted'
                    diff='_Diff'
                        
                data = self.datasets[data_name]
            except:
                raise FileNotFoundError('File does not exist')

        # replace inf with nan, drop columns with NA
        data.replace(np.inf, np.nan, inplace=True)
        data.dropna(axis=1, how='all', inplace=True)

        LONGS, SHORTS = [],[]
        R_LONGS, R_SHORTS = [], []
        for date in data.columns:
            if momentum:
                bonds_picked = self._create_single_momentum_portfolio(date)
            elif low_risk:
                bonds_picked = self._create_single_lowrisk_portfolio(date)
            else:
                bonds_picked = self._create_single_portfolio(data, date)
                
            LONGS.append(bonds_picked['long'])
            SHORTS.append(bonds_picked['short'])
            
            # FINALLY - calculate return!! exciting again
            R_LONGS.append([self._calculate_return_on_bond(bond, 'long', date) for bond in bonds_picked['long']])
            R_SHORTS.append([self._calculate_return_on_bond(bond, 'short', date) for bond in bonds_picked['short']])
            print(f"Experiment no.{self.experiment} - Returns for {date} calculated.")
        
        # save created porfolios and returns for any future use
        if momentum or low_risk:
            if momentum:
                base = 'momentum'
            else:
                base = 'low_risk'
            [self.save_other_portfolio(portfolio, data.columns, pname, base) for portfolio, pname in zip([LONGS, SHORTS], ['LONGS', 'SHORTS'])]
            [self.save_other_portfolio_returns(portfolio, data.columns, pname, base) for portfolio, pname in zip([R_LONGS, R_SHORTS], ['LONGS', 'SHORTS'])]
        else:
            [self.save_portfolio(portfolio, data.columns, pname, sentiment_base, creation_period, diff, w_name) for portfolio, pname in zip([LONGS, SHORTS], ['LONGS', 'SHORTS'])]
            [self.save_portfolio_returns(portfolio, data.columns, pname, sentiment_base, creation_period, diff, w_name) for portfolio, pname in zip([R_LONGS, R_SHORTS], ['LONGS', 'SHORTS'])]   
            

    def load_datasets(self, data_path):
        self.files = [f for f in listdir(data_path) if isfile(join(data_path, f))]
        self.datasets = {f: pd.read_csv(join(data_path, f), index_col=0) for f in self.files}
        return self.datasets
    
    def save_portfolio(self, portfolio, columns, portfolio_name, sentiment_base, creation_period, diff, weighted):
        portfolio_df = pd.DataFrame(portfolio).T
        portfolio_df.columns = columns
        fname = f"{portfolio_name}_{self.market_index}_{sentiment_base}_{creation_period}{diff}{weighted}.csv"
        fpath = join(self.output_path, fname)
        portfolio_df.to_csv(fpath)
    
    def save_other_portfolio(self, portfolio, columns, portfolio_name, base):
        portfolio_df = pd.DataFrame(portfolio).T
        portfolio_df.columns = columns
        fname = f"{portfolio_name}_{self.market_index}_{base}.csv"
        fpath = join(self.output_path, fname)
        portfolio_df.to_csv(fpath)
    
    def save_portfolio_returns(self, portfolio, columns, portfolio_name, sentiment_base, creation_period, diff, weighted):
        portfolio_df = pd.DataFrame(portfolio).T
        portfolio_df.columns = columns
        fname = f"RETURNS_{portfolio_name}_{self.market_index}_{sentiment_base}_{creation_period}{diff}{weighted}.csv"
        fpath = join(self.output_path, fname)
        portfolio_df.to_csv(fpath)

    def save_other_portfolio_returns(self, portfolio, columns, portfolio_name, base):
        portfolio_df = pd.DataFrame(portfolio).T
        portfolio_df.columns = columns
        fname = f"RETURNS_{portfolio_name}_{self.market_index}_{base}.csv"
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
                interest = float(specific_bond[specific_bond.Date.apply(lambda x: x.month)==month]['Month_Interest_rate'])
                return np.round(
                    (100*end_price/buy_price - 100 + interest) / 100, 4 # we consider 100 to be fixed investment to easily calculate interest
                )
            except:
                return 0

        elif long_short == 'short':
            try:
                sell_price = float(specific_bond[specific_bond.Date.apply(lambda x: x.month)==month]['Bid_price'])
                end_price = float(specific_bond[specific_bond.Date.apply(lambda x: x.month)==month_t]['Bid_price'])
                interest = float(specific_bond[specific_bond.Date.apply(lambda x: x.month)==month]['Month_Interest_rate'])
                return np.round(
                    (100 - 100*end_price/sell_price) / 100, 4 # we consider 100 to be fixed investment to easily calculate interest
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

    def _create_single_lowrisk_portfolio(self, date):
        # 1. extract year and month
        year, month = [int(x) for x in date.split('-')][:2]

        # 2. Extract considered companies from bond dataset
        actual_bonds = (
            self.bond_dataset[(self.bond_dataset.Date.apply(lambda x: x.year)==year) & (self.bond_dataset.Date.apply(lambda x: x.month)==month)]
        )

        # 3. Select bonds
        actual_bonds = (
            actual_bonds[actual_bonds.TTM > 1/12] # just to safely filter those bonds maturing that month
            .sort_values('TTM')
        ).reset_index()

        BONDS_picked = {
            'long': list(actual_bonds['Bond'][:self.decile_size[self.market_index]]),
            'short': list(actual_bonds['Bond'][-self.decile_size[self.market_index]:])
        }
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
        )[['Bond', 'Month_Interest_rate','Date', 'Ask_price', 'Bid_price']]
        actual_bonds['Price'] = (actual_bonds['Ask_price'] + actual_bonds['Bid_price']) / 2

        # 3. Filter corresponding bonds and their records 3 months back
        actual_bonds_3M = self.bond_dataset[self.bond_dataset.Bond.isin(actual_bonds.Bond)]
        actual_bonds_3M = (
            actual_bonds_3M[(actual_bonds_3M.Date.apply(lambda x: x.year)==year_t) & (actual_bonds_3M.Date.apply(lambda x: x.month)==month_t)]
        )[['Bond', 'Month_Interest_rate', 'Date', 'Ask_price', 'Bid_price']]
        actual_bonds_3M.rename(columns={
            'Ask_price': 'Ask_price_t',
            'Bid_price': 'Bid_price_t'
        }, inplace=True)
        actual_bonds_3M['Price_t'] = (actual_bonds_3M['Ask_price_t'] + actual_bonds_3M['Bid_price_t']) / 2

        # 4. Calculate returns
        ## Drop date & months_interest rate not to cramp join
        actual_bonds.drop(['Date', 'Month_Interest_rate'], axis=1, inplace=True), actual_bonds_3M.drop('Date', axis=1, inplace=True)
        
        bonds_join = (
            actual_bonds.set_index('Bond')
            .join(actual_bonds_3M.set_index('Bond'), on='Bond')
        )
        returns = (
            (bonds_join['Price'] - bonds_join['Price_t']) / bonds_join['Price_t'] + bonds_join['Month_Interest_rate']
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
        self.weighted = (True if kwargs['weighted'] else False)