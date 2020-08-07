"""
File: 1. DB to CSV.py
Author: Daniel Stancl

Description: This file contains the source code for extracting the records
from the up-to-date SQL/Django database and store them in CSV files.
"""

# 1. Import libraries and define helper functions
from datetime import datetime
import numpy as np
import pandas as pd
import django
from set_django_db import set_django_db

# 2. DB_to_CSV function
class DB_to_CSV():
    def __init__(self, Company, Review):
        self.Company = Company
        self.Review = Review

    def run(self, company_filename, review_filename):
        """
        High level implementation of transforming DB records into the CSV.
        """
        companies = self._companiesToDF()
        reviews = self._reviewsToDF()
        reviews = self._mergeReviewsWithCompanies(reviews, companies)
        reviews['Date'] = self._generateDateColumn(reviews)
        reviews['Year-Month'] = self._generateYM_Column(reviews)
        self._save(
            companies, company_filename,
            reviews, review_filename
        )

    ### HELPER FUNCTIONS ###
    def _companiesToDF(self):
        companies = pd.DataFrame(
            list(
                self.Company
                .objects
                .values('id', 'Company', 'Sector', 'ListedOn')
                .all()
            )
        )
        return companies

    def _reviewsToDF(self):
        reviews = pd.DataFrame(
            list(
                self.Review
                .objects
                .values(
                    'id', 'Company_id', 'ReviewTitle', 'Rating',
                    'JobTitle', 'EmployeeRelationship',
                    'Contract', 'Pros', 'Cons',
                    'Year', 'Month', 'Day')
                .all()
            )
        )
        return reviews

    def _mergeReviewsWithCompanies(self, reviews, companies):
        reviews = reviews.merge(
            companies[['id', 'Company', 'Sector', 'ListedOn']].rename(columns={'id': 'Company_id'}),
            on='Company_id'
        )
        return reviews

    def _generateDateColumn(self, reviews):
        Date = reviews.apply(lambda x: '-'.join(
            [str(x['Year']), str(x['Month']), str(x['Day'])]
            ), axis=1
        )
        return np.array(
            self._string_to_date(date) for date in Date
        )

    def _generateYM_Column(self, reviews):
        return reviews.apply(lambda x: self._string_to_YM('-'.join(
            [str(x['Year']), str(x['Month'])])
            ), axis=1
        )

    def _save(self, companies, company_filename, reviews, review_filename):
        companies.to_csv(company_filename)
        reviews.to_csv(review_filename)
    
    def _string_to_date(self, date_str):
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except:
            return datetime.strptime('1800-1-1', '%Y-%m-%d')
        
    def _string_to_YM(self, date_str):
        try:
            return datetime.strptime(date_str, '%Y-%m')
        except:
            return datetime.strptime('1800-1-1', '%Y-%m-%d')