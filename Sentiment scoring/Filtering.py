"""
File: Filtering.py
Author: Daniel Stancl

Description: This file contains the source code for filtering reviews
w.r.t. date and a count.
"""
import numpy as np
import pandas as pd
from datetime import datetime

class Filter(object):
    def __init__(self, companies, reviews):
        self.companies = companies
        self.reviews = reviews
    
    def run(self, min_date, max_date, min_reviews):
        self._dateFiltering(min_date, max_date)
        self._dropNegligible(min_reviews)
        return self.companies, self.reviews

    def _dateFiltering(self, min_date, max_date):
        return pd.DataFrame(
            self.reviews[(self.reviews.Date >= min_date) & (self.reviews.Date <= max_date)]
        )

    def _dropNegligible(self, min_reviews):
        """
        Function that retains only companies with at least `min_reviews` reviews in a monitored period.
        Accordingly, the reviews of companies with too little reviews are to be dropped as well.
        """ 
        # count reviews
        reviews_count = (
            self.reviews
            .groupby('Company')
            .Rating
            .count()
        )
        companies_filtered = list(reviews_count[reviews_count>10].index)

        self.companies = self.companies[self.companies.Company.isin(companies_filtered)]
        self.reviews = self.reviews[self.reviews.Company.isin(companies_filtered)]
        

