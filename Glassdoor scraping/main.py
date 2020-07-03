# import libraries
import time
import datetime
from argparse import ArgumentParser
from datetime import date
import re
import json
import numpy as np
import pandas as pd
import django
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from GlassdoorScraper import GlassdoorScraper
from set_django_db import set_django_db

# parameters/arguments
parser = ArgumentParser()

parser.add_argument(
    '--chrome_driver_path',
    default='/mnt/c/Data/UCL/@MSC Project - Data and sources/chromedriver.exe',
    help='An absolute path to the ChromeDriver.'
)

parser.add_argument(
    '--headless',
    action='store_true',
    help='If --headless is passed in, the `headless` browsing is used.'
)

parser.add_argument(
    '--email',
    help='Email used for log in to the Glassdoor account.'
)

parser.add_argument(
    '-p', '--password',
    help='Password used for log in to the Glassdoor account.'
)

parser.add_argument(
    '-c', '--credentials',
    default='/mnt/c/Data/UCL/@MSc Project - Data and sources/credentials.json',
    help='Path to credential file containing email and password\
        used for log in to the Glassdoor account.'
)

parser.add_argument(
    '--companies',
    help="An absolute path to the list of companies (txt file)."
)

parser.add_argument(
    '-u', '--url',
    help='An absolute path to the list of  URL address (txt file)\
        to the landing page of reviews for a given company.'
)

parser.add_argument(
    '--location',
    default='London',
    help="A location we are interested in.\
        Default='London'"
)

parser.add_argument(
    '--max_review_age',
    help='An indication how old reviews are to be scraped.\
        Define if min_date is not provided.'
)

parser.add_argument(
    '--min_date',
    help="An indication up to which date reviews are to be scraped.\
        format='yyyy-mm-dd'\
        Define iff max_review_age is not provided."
)

parser.add_argument(
    '--mysite_path',
    default='/mnt/c/Data/UCL/@MSc Project/DB/mysite/',
    help='An absolute path to the django application containing models for the DB.\
        This is required iff output_path is not passed in.'
)

parser.add_argument(
    '--output_path',
    help='An absolute path of the output csv/xlsx file storing the scraped data.\
        This is required iff mysite_path is not passed in.'
)

parser.add_argument(
    '-l', '--limit',
    help='A number of pages to be scraped.\
        This is an ideal option for testing, otherwise no limit is passed.'
)

args = parser.parse_args()

# some value assignments and sanity checks

## credentials
if args.credentials:
    try:
        with open(args.credentials) as f:
            credentials = json.loads(f.read())
            args.email = credentials['email']
            args.password = credentials['password']
    except FileNotFoundError:
        raise Exception('The filepath given does not exist.')
else:
    try:
        args.email, args.password = args.email, args.password # a simple way how to verify whether email and password were passed in
    except ValueError:
        raise Exception('Neiter filepath to the credentials, nor email and password are specified.\
            Please, provide either path to the fiel with credentials or email/password directly to cmd.')

## file path to the txt file with companies
if args.companies:
    try:
        with open(args.companies, 'r') as f:
            companies = [line.strip() for line in f]
        print(f"{len(companies)} companies are to be scraped.")
    except FileNotFoundError:
        raise Exception('The filepath given does noe exist or the format of the file is not appropriate')
else:
    raise Exception('Filepath to the text file containing companies must be provided.')

## if url provided, the length of the url file and companies file must be the same
if args.url:
    if args.companies:
        pass
    else:
        raise Exception('Both parameters companies and url must be given.')

## min_date | max_reivew_age
if (args.min_date!=None) & (args.max_review_age!=None):
    raise Exception('Only one parameter out of min_date and max_review_age can be specified!')

## file path to the output files
if args.output_path:
    file_type = args.output_path.split('.')[-1]
    if file_type not in ['csv', 'xlsx', 'xls']:
        raise Exception('Invalid file path format.')

if args.limit:
    try:
        args.limit = int(args.limit) 
    except Exception:
        raise TypeError('Limit must be a type of an integer!.')
else:
    args.limit = float(np.inf)

#######################
##### APPLICATION #####
#######################
def main():
    if args.mysite_path :
        # import Company - django.db.models.Model
        set_django_db(mysite_path=args.mysite_path)
        from tables_daniel.models import Review, Company
    else:
        Review = None

    scraper = GlassdoorScraper(
        chrome_driver_path=args.chrome_driver_path,
        email=args.email,
        password=args.password,
        headless_browsing=args.headless,
        review_writer=Review,
        company_reader=Company,
        max_review_age=args.max_review_age,
        min_date=args.min_date
    )
    
    for company_name in companies:
        scraper.getOnReviewsPage( 
            company_name=company_name,
            location=args.location,
            url=url
        )
        scraper.acceptCookies()
        scraper.scrape(
            company_name=company_name,
            location=args.location,
            limit=args.limit
        )

if __name__=='__main__':
    main()