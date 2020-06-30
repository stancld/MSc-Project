# set hyperparameters
from Scraper_setup import *

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
scraper = GlassdoorScraper(path_chrome_driver, email, account_type='email')


#companies = [
#    'Intel Corporation', 'Nvidia Corporation', 'Amazon', 'Advanced Micro Devices', 'Western Digital'
#]

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

#######################
#######################
#######################
path = '/mnt/c/Data/FAM_reviews.xlsx'
scraper.data.to_excel(
    path
)
