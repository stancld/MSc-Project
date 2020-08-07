"""
File: 1. DB to CSV.py
Author: Daniel Stancl

Description: This file contains the script for running various code files
responsible for loading all reviews and companeis records from the DB.
Subsequently, the data are filtered and sentiment scores are computed.
"""

# Import libraries
import time
from datetime import datetime
from argparse import ArgumentParser
import numpy as np
import pandas as pd
import django
from set_django_db import set_django_db

# Import own functions/classes
from DB_to_CSV import DB_to_CSV

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
    default='/mnt/c/Data/UCL/@MSc Project - Data and Sources/companies.csv',
    help='An absolute path of an ouptut CSV files containing companies.'
)

parser.add_argument(
    '--review_path',
    default='/mnt/c/Data/UCL/@MSc Project - Data and Sources/reviews.csv',
    help='An absolute path of an ouptut CSV files containing revies.'
)

args = parser.parse_args()

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
    writer = DB_to_CSV(Company, Review)
    writer.run(args.company_path, args.review_path)
    print('CSV files were succesfully created.')

    # 2. Filtering - Drop companies with less than 10 reviews in total

if __name__=='__main__':
    main()