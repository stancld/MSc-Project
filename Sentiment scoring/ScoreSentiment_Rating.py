"""
File: ScoreSentiment_Rating.py
Author: Daniel Stancl

Description: This file takes companies and reviews dataframe and generate
columns with employee sentiment for companies in a given month/ over a given period etc.
"""
import pandas as pd


class ScoreSentiment_Rating(object):
    def __init__(self, companies, reviews):
        self.companies = companies
        self.reviews = reviews
    
    def run(self, sentiment_path, periods, difference):
        self.sentimentMonthly(sentiment_path, difference)
        [self.sentimentCustom(period, sentiment_path, difference) for period in periods]

    def sentimentMonthly(self, sentiment_path, difference, _return=False):
        sentiment = pd.DataFrame(
            pd.DataFrame(
                self.reviews
                .groupby(['Company', 'Year-Month'])
                .Rating
                .agg(['mean', 'count'])
            ).to_records()
        )
        sentiment.columns = ['Company', 'Year-Month', 'Rating', 'Count']

        self.sentiment_rating = pd.pivot_table(sentiment, 'Rating', index='Company', columns='Year-Month', fill_value=None)
        self.sentiment_count = pd.pivot_table(sentiment, 'Count', index='Company', columns='Year-Month', fill_value=0)

        # save
        fname = f"{sentiment_path}Sentiment_Rating_1M.csv"
        self.sentiment_rating.to_csv(fname)

        fname = f"{sentiment_path}Sentiment_Count_1M.csv"
        self.sentiment_count.to_csv(fname)

        # compute difference
        if difference:
            sentiment_diff = self._sentimentDifference(
                data=self.sentiment_rating,
            )
            fname = f"{sentiment_path}Sentiment_Rating_Diff_1M.csv"
            sentiment_diff.to_csv(fname)

        if _return:
            return self.sentiment_rating, self.sentiment_count, self.sen

    def sentimentCustom(self, period, sentiment_path, difference, _return=False):
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
        
        fname = f"{sentiment_path}Sentiment_Rating_{period}M.csv"
        rollingSentiment.to_csv(fname)

        # compute difference
        if difference:
            sentiment_diff = self._sentimentDifference(
                data=rollingSentiment
            )
            fname = f"{sentiment_path}Sentiment_Rating_Diff_{period}M.csv"
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

        