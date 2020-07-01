# setup
import os
import sys
from argparse import ArgumentParser
from WikiScraper import *
from set_django_db import set_django_db

# parameters
parser = ArgumentParser()

parser.add_argument(
    '--stock_indices',
    default=['S&P 500', 'FTSE 100', 'EURO STOXX 50'],
    help="Pass a list of stock indices you would like to scrape.\
        Currently supported are: ['S&P 500', 'FTSE 100', 'EURO STOXX 50']."
)

parser.add_argument(
    '--mysite_path',
    default='/mnt/c/Data/UCL/@MSc Project/DB/mysite/',
    help='An absolute path to a Django app.'
)

args = parser.parse_args()

#######################
##### APPLICATION #####
#######################
def main(): 
    # import Company - django.db.models.Model
    set_django_db(mysite_path=args.mysite_path)
    from tables_daniel.models import Company

    wikiScraper = WikiScraper(CompanyWriter=Company)
    for stock_index in args.stock_indices:
        wikiScraper.scrapeWikipedia(stock_index)
    wikiScraper.scrapeYahooFinance()
    wikiScraper.writeToDjangoDB()

if __name__=='__main__':
    main()