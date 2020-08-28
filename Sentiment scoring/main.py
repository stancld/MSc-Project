"""
Author: Daniel Stancl

Description: This file contains the script for running various code files
responsible for loading all reviews and companeis records from the DB.
Subsequently, the data are filtered and sentiment scores are computed.
"""

# Import libraries
from os.path import join
import time
from datetime import datetime
from argparse import ArgumentParser
import numpy as np
import pandas as pd
import django
from set_django_db import set_django_db

# Import own functions/classes
from DB_to_CSV import DB_to_CSV
from Filtering import Filter
from ScoreSentiment import ScoreSentiment

# parameters/arguments
parser = ArgumentParser()

parser.add_argument(
    '--mysite_path',
    default='/mnt/c/Data/UCL/@MSc Project/DB/mysite/',
    help='An absolute path to the django application containing models for the DB.\
        This is required iff output_path is not passed in.'
)

parser.add_argument(
    '--company_path',
    default='/mnt/c/Data/UCL/@MSc Project - Data and Sources/Sentiment results/New/source/companies.csv',
    help='An absolute path of an ouptut CSV files containing companies. Possibly input file if DB_to_CSV is not run.'
)

parser.add_argument(
    '--review_path',
    default='/mnt/c/Data/UCL/@MSc Project - Data and Sources/Sentiment results/New/source/reviews.csv',
    help='An absolute path of an ouptut CSV files containing reviews. Possibly input file if DB_to_CSV is not run.'
)

parser.add_argument(
    '--sentiment_path',
    default='/mnt/c/Data/UCL/@MSc Project - Data and Sources/Sentiment results/New/',
    help='An absolute path of an ouptut CSV files containing sentiment results.'
)

parser.add_argument(
    '--min_date',
    default='2018-07-01',
    help='The minimum date in format of `yyyy-mm-dd`'
)

parser.add_argument(
    '--max_date',
    default='2020-06-30',
    help='The maximum date in format of `yyyy-mm-dd`'
)

parser.add_argument(
    '--min_reviews',
    default=10,
    help='All companies having less than `min_reviews` reviews are to be dropped.'
)

parser.add_argument(
    '--periods',
    help='Pass length of rolling windows used for calculating sentiment over longer than month period\
        format=string with | used as delimeters, i.e. "3 | 4 | 6"'

)

parser.add_argument(
    '-D', '--difference',
    action='store_true',
    help='Indication whether difference should be computed.'
)

parser.add_argument(
    '-W', '--weighted',
    action='store_true',
    help='Indication whether weighted sentiment score should be computed.'
)

parser.add_argument(
    '--db_to_csv',
    action='store_true',
    help='Indication whether DB_to_CSV to be run'
)

args = parser.parse_args()

# change str format of min/max_date to datetime format
args.min_date = datetime.strptime(args.min_date,'%Y-%m-%d')
args.max_date = datetime.strptime(args.max_date,'%Y-%m-%d')

# parse periods 
try:
    periods = [int(period.strip()) for period in args.periods.split('|')]
except:
    periods = []

#######################
##### APPLICATION #####
#######################

def main():
    try:
        set_django_db(args.mysite_path)
        from tables_daniel.models import Company, Review
    except Exception as e:
        print(f'Error {e}\ a.k.a. Invalid mysite_path.')

    # 1. Save Djamgo DB records to CSV files.
    if args.db_to_csv:
        writer = DB_to_CSV(Company, Review)
        companies, reviews = writer.run(args.company_path, args.review_path, save=True)
    else:
        companies = pd.read_csv(args.company_path)
        reviews = pd.read_csv(args.review_path)
        reviews['Date'] = pd.to_datetime(reviews['Date'])

    print('1/3 Done - CSV files were succesfully created.')

    # 2. Filtering - Drop companies with less than 10 reviews in total
    if args.db_to_csv:
        filtering = Filter(companies, reviews)
        companies, reviews = filtering.run(args.min_date, args.max_date, args.min_reviews, args.sentiment_path)
    print('2/3 Done - Filtering was completed.')

    # 3. Employee sentiment
    scoreSentiment = ScoreSentiment(companies, reviews)
    #for sentiment_base in ['Rating', 'Reviews_Sentiment']:
    #    scoreSentiment.run(args.sentiment_path, sentiment_base, periods, args.difference, False)
    scoreSentiment.run(args.sentiment_path, 'Reviews_Sentiment', periods, args.difference, True)
    print('3/3 Done - Sentiment was scored.')   

if __name__=='__main__':
    main()
