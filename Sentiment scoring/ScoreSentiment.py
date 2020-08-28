"""
File: ScoreSentiment.py
Author: Daniel Stancl

Description: This file takes companies and reviews dataframe and generate
columns with employee sentiment for companies in a given month/ over a given period etc.

utf-8
"""
import numpy as np
import pandas as pd

class ScoreSentiment(object):
    def __init__(self, companies, reviews):
        self.companies = companies
        self.reviews = reviews
        self.base_to_name = {
            'Rating': 'Rating',
            'Reviews_Sentiment': 'Reviews'
        }
    
    def run(self, sentiment_path, sentiment_base, periods, difference, weighted):
        if sentiment_base not in ['Rating', 'Reviews_Sentiment']:
            raise ValueError("Arg sentiment_base must be either 'Rating' or 'Reviews_Sentiment'.")
        if weighted:
            self.sentimentMonthly_weighted(sentiment_path, difference)
            [self.sentimentCustom(period, sentiment_path, sentiment_base, difference, weighted) for period in periods]
        else:
            self.sentimentMonthly(sentiment_path, sentiment_base, difference)
            [self.sentimentCustom(period, sentiment_path, sentiment_base, difference, weighted) for period in periods]

    def sentimentMonthly(self, sentiment_path, sentiment_base, difference, _return=False):
        if sentiment_base == 'Rating':
            sentiment = pd.DataFrame(
                pd.DataFrame(
                    self.reviews
                    .groupby(['Company', 'Year-Month'])
                    .Rating
                    .agg(['mean', 'count'])
                ).to_records()
            )
            sentiment.columns = ['Company', 'Year-Month', 'Rating', 'Count']
        elif sentiment_base == 'Reviews_Sentiment':
            sentiment = pd.DataFrame(
                pd.DataFrame(
                    self.reviews
                    .groupby(['Company', 'Year-Month'])
                    .Reviews_Sentiment
                    .agg(['mean', 'count'])
                ).to_records()
            )
            sentiment.columns = ['Company', 'Year-Month', 'Reviews_Sentiment', 'Count']

        self.sentiment_rating = pd.pivot_table(sentiment, sentiment_base, index='Company', columns='Year-Month', fill_value=None)
        self.sentiment_count = pd.pivot_table(sentiment, 'Count', index='Company', columns='Year-Month', fill_value=0)

        # save
        fname = f"{sentiment_path}Sentiment_{self.base_to_name[sentiment_base]}_1M.csv"
        self.sentiment_rating.to_csv(fname)

        fname = f"{sentiment_path}Sentiment_Count_1M.csv"
        self.sentiment_count.to_csv(fname)

        # compute difference
        if difference:
            sentiment_diff = self._sentimentDifference(
                data=self.sentiment_rating,
            )
            fname = f"{sentiment_path}Sentiment_{self.base_to_name[sentiment_base]}_Diff_1M.csv"
            sentiment_diff.to_csv(fname)

        if _return:
            return self.sentiment_rating, self.sentiment_count

    def sentimentMonthly_weighted(self, sentiment_path, difference, _return=False):
        """
        Works only with reviews
        """
        self.reviews['WeightedSentiment'] = self.reviews['ReviewLength'] * self.reviews['Reviews_Sentiment']
        
        # 1. Compute total sentiment
        sentiment = pd.DataFrame(
            pd.DataFrame(
                self.reviews
                .groupby(['Company', 'Year-Month'])
                .Reviews_Sentiment
                .agg(['mean', 'count'])
            ).to_records()    
        )
        sentiment.columns = ['Company', 'Year-Month', 'Reviews_Sentiment', 'Count']

        # 2. Sum weights
        sentiment_weigth = pd.DataFrame(
            pd.DataFrame(
                self.reviews
                .groupby(['Company', 'Year-Month'])
                .ReviewLength
                .sum()
            ).to_records()    
        )
        sentiment_weigth.columns = ['Company', 'Year-Month', 'Weigth']

        # 3. Compute weighted sentiment and replace inf values resulting from a division by 0
        sentiment['WeightedSentiment'] = sentiment['Reviews_Sentiment'] / sentiment_weigth['Weigth']
        sentiment['WeightedSentiment'].replace(np.inf, 0, inplace=True)

        self.sentiment_rating = pd.pivot_table(sentiment, 'WeightedSentiment', index='Company', columns='Year-Month', fill_value=None)
        self.sentiment_count = pd.pivot_table(sentiment, 'Count', index='Company', columns='Year-Month', fill_value=0)

        # 4. save
        fname = f"{sentiment_path}SentimentWeighted_Reviews_1M.csv"
        self.sentiment_rating.to_csv(fname)

        # DIFFERENCE
        # compute difference
        if difference:
            sentiment_diff = self._sentimentDifference(
                data=self.sentiment_rating,
            )
            fname = f"{sentiment_path}SentimentWeighted_Reviews_Diff_1M.csv"
            sentiment_diff.to_csv(fname)

    def sentimentCustom(self, period, sentiment_path, sentiment_base, difference, weighted, _return=False):
        sentimentSums = self.sentiment_count * self.sentiment_rating
        
        rollingCounts = (
            self.sentiment_count
            .T
            .rolling(window=period)
            .sum()
            .T
        )
        
        rollingSums = (
            sentimentSums
            .fillna(0)
            .T
            .rolling(window=period)
            .sum()
            .T
            .replace(
                to_replace=0,
                value=None
            )
        )

        rollingSentiment = rollingSums / rollingCounts
        
        # save:
        if weighted:
            w_name = 'Weighted'
        else:
            w_name = ''
        fname = f"{sentiment_path}Sentiment_{self.base_to_name[sentiment_base]}{w_name}_{period}M.csv"
        rollingSentiment.to_csv(fname)

        fname = f"{sentiment_path}Sentiment_Count_3M.csv"
        rollingCounts.to_csv(fname)

        # compute difference
        if difference:
            sentiment_diff = self._sentimentDifference(
                data=rollingSentiment
            )
            fname = f"{sentiment_path}Sentiment_{self.base_to_name[sentiment_base]}{w_name}_Diff_{period}M.csv"
            sentiment_diff.to_csv(fname)

        if _return:
            return rollingSentiment, sentiment_diff

    def _sentimentDifference(self, data):
        sentimentDiff = (
            data
            .T
            .rolling(window=2)
            .apply(lambda x: self._diff_function(x))
            .T
        )
        return sentimentDiff
    
    def _diff_function(self, x):
        return x.iloc[1] - x.iloc[0]