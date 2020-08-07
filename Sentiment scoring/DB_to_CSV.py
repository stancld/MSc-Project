"""
File: DB_to_CSV.py
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

    def run(self, company_filename, review_filename, save=False):
        """
        High level implementation of transforming DB records into the CSV.
        """
        self._companiesToDF()
        self._reviewsToDF()
        self._mergeReviewsWithCompanies()
        
        self.reviews['Review'] = self._generateReviewColumn()
        self.reviews['ReviewLentgth'] = self._generateReviewLengthColumn()
        self.reviews['Date'] = self._generateDateColumn()
        self.reviews['Year-Month'] = self._generateYM_Column()

        self.reviews['EmployeeRelationship'] = [self._update_EmployeeRelationship(self.reviews.loc[row, 'EmployeeRelationship']) for row in self.reviews.index]
        
        if save==True:
            self._save(company_filename, review_filename)
        else:
            pass
        return self.companies, self.reviews

    ### HELPER FUNCTIONS ###
    def _companiesToDF(self):
        self.companies = pd.DataFrame(
            list(
                self.Company
                .objects
                .values('id', 'Company', 'Sector', 'ListedOn')
                .all()
            )
        )

    def _reviewsToDF(self):
        self.reviews = pd.DataFrame(
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

    def _mergeReviewsWithCompanies(self):
        self.reviews = self.reviews.merge(
            self.companies[['id', 'Company', 'Sector', 'ListedOn']].rename(columns={'id': 'Company_id'}),
            on='Company_id'
        )

    def _generateDateColumn(self):
        Date = self.reviews.apply(lambda x: '-'.join(
            [str(x['Year']), str(x['Month']), str(x['Day'])]
            ), axis=1
        )
        return np.array(
            [self._string_to_date(date) for date in Date]
        )

    def _generateYM_Column(self):
        return self.reviews.apply(lambda x: self._string_to_YM('-'.join(
            [str(x['Year']), str(x['Month'])])
            ), axis=1
        )

    def _generateReviewColumn(self):
        return self.reviews['Pros'] + ' ' + self.reviews['Cons']
    
    def _generateReviewLengthColumn(self):
        return self.reviews['Review'].apply(lambda x: len(x))

    def _update_EmployeeRelationship(self, x):
        """
        Fix employee relationship as sometimes, parsing problems etc may occur.
        """
        if x not in ['Current Employee', 'Former Employee']:
            return 'Not specified'
        else:
            return x

    def _save(self, company_filename, review_filename):
        self.companies.to_csv(company_filename)
        self.reviews.to_csv(review_filename)
    
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