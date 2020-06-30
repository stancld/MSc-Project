# import libraries
import time
import datetime
from datetime import date
import re
import numpy as np
import pandas as pd
import django
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from GlassdoorScraper import GlassdoorScraper


#######################
##### APPLICATION #####
#######################

# application (still needs to be automated in scrape module)
if __name__=='__main__':
    from Scraper_setup import *
    exec(open('set_django_db.py').read())
    from tables_daniel.models import Review

    scraper = GlassdoorScraper(path_chrome_driver, email, account_type='email', review_writer=Review)
    companies = ['Facebook', 'Apple', 'Microsoft Corporation']

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
