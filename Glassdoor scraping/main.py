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

# parameters/arguments
parser = ArgumentParser()

parser.add_argument(
    '--chrome_driver_path',
    default='/mnt/c/Data/UCL/@MSC Project - Data and sources/chromedriver.exe',
    help='An absolute path to the ChromeDriver that is necessary for web scraping.'
)
parser.add_argument(
    '--account_type',
    default='email',
    help="An indication which type of account is used for log in to the Glassdoor portal.\
        Currently supported: `['email', 'gmail']`"
)
parser.add_argument(
    '--email',
    help='Email used for log in to the Glassdoor account'
)
parser.add_argument(
    '-p', '--password',
    help='Password used for log in to the Glassdoor account'
)
parser.add_argument(
    'c', '--credentials',
    help='Path to credential file containing email and password\
        used for lod in to the Glassdoor account.'
)
parser.add_argument(
    '--headless',
    default='store_false',
    action='store_true',
    help='If --headless is passed in, the `headless` browsing is used.'
)

args = parser.parse_args()

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

#######################
##### APPLICATION #####
#######################
def main():
    from Scraper_setup import path_chrome_driver, url, email, password, account_type, location
    
    exec(open('set_django_db.py').read())
    from tables_daniel.models import Review

    companies = ['Facebook', 'Apple']

    scraper = GlassdoorScraper(
        chrome_driver_path=arg.chrome_driver_path,
        account_type=args.account_type,
        email=args.email,
        password=args.password

        path_chrome_driver, email, account_type='email', password=password, review_writer=Review)
    
    for company_name in companies:
        scraper.getOnReviewsPage( 
            company_name=company_name,
            location=location    
        )
        scraper.acceptCookies()
        scraper.scrape(
            company_name=company_name,
            location=location,
        )

if __name__=='__main__':
    main()