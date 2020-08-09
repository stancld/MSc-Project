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
    
    def run(self, sentiment_path, periods):
        self.sentimentMonthly(sentiment_path)
        [self.sentimentCustom(period, sentiment_path) for period in periods]

    def sentimentMonthly(self, sentiment_path, _return=False):
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

        if _return:
            return self.sentiment_rating, self.sentiment_count

        # save
        fname = f"{sentiment_path}Sentiment_Rating_1M.csv"
        self.sentiment_rating.to_csv(fname)

        fname = f"{sentiment_path}Sentiment_Count_1M.csv"
        self.sentiment_count.to_csv(fname)

    def sentimentCustom(self, period, sentiment_path, _return=False):
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

        if _return:
            return rollingSentiment