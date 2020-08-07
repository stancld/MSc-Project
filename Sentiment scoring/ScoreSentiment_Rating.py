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
    
    def run(self):
        pass