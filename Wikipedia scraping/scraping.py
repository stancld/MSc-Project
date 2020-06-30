# setup
import os
from WikiScraper import *

# import Company - django.db.models.Model
cwd = os.getcwd()
exec(open('set_django_db.py').read())
from tables_daniel.models import Company
os.chdir(cwd)

# parameters
stock_indices = ['S&P 500', 'FTSE 100', 'EURO STOXX 50']

stock_indices = ['EURO STOXX 50']
#######################
##### APPLICATION #####
#######################
wikiScraper = WikiScraper()
for stock_index in stock_indices:
    wikiScraper.scrapeWikipedia(stock_index)
wikiScraper._scrapeYahooFinance_()


wikiScraper.data


