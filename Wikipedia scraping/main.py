# setup
import os
import sys
import pandas as pd
from argparse import ArgumentParser
from WikiScraper import *
from set_django_db import set_django_db

# parameters/arguments
parser = ArgumentParser()

parser.add_argument(
    '--stock_indices',
    help="A list of stock indices that should be scraped.\
        Currently supported: `['S&P 500', 'FTSE 100', 'EURO STOXX 50']`."
)

parser.add_argument(
    '--companies',
    help="A path to the list of companies that should be scraped from Yahoo Finance.\
        The companies should be provided in an excel file with 3 columns:\
            'Company', 'Symbol', 'ListedOn'."
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

args = parser.parse_args()

# sanity checks
if (args.mysite_path!=None) & (args.output_path!=None):
    raise Exception(
        'mysite_path!=None and output_path!=None is not compatible\
            because output_path is used iff mysite_path=None.'
    )
if (args.mysite_path==None) & (args.output_path==None):
    raise Exception(
        'mysite_path==None and output_path==None is not compatible\
            because output_path has no default value while must be specified.'
    )
if args.companies:
    if args.companies.split('.')[-1] not in ['xls, xlsx']:
        raise Exception(
            'Invalid file format provided'
        )
if (args.stock_indices!=None) & (args.companies!=None):
    raise Exception(
        'Only either stock_indices or companies are allowed to be specified.\
            Not both of them at once.'
    )
if (args.stock_indices==None) & (args.companies==None):
    raise Exception(
        'Exactly stock_indices or companies must be specified.'
    )

# parse stock_indices
if (args.stock_indices != ['S&P 500', 'FTSE 100', 'EURO STOXX 50']) & (args.stock_indices!=None):
    args.stock_indices = args.stock_indices.strip('[').strip(']').split(',')
    args.stock_indices = [stock_index.strip().strip("'") for stock_index in args.stock_indices]

# Open companies
companies = pd.read_excel(companies).to_dict('records')

#######################
##### APPLICATION #####
#######################
def main(): 
    if args.mysite_path:
        # import Company - django.db.models.Model
        set_django_db(mysite_path=args.mysite_path)
        from tables_daniel.models import Company

        wikiScraper = WikiScraper(CompanyWriter=Company)
    else:
        wikiScraper = WikiScraper()

    if args.stock_indices:
        for stock_index in args.stock_indices:
            wikiScraper.scrapeWikipedia(stock_index)
    elif args.companies:
        wikiScraper.data.extend(companies)

    wikiScraper.scrapeYahooFinance()
    
    if args.mysite_path:
        wikiScraper.writeToDjangoDB()
    else:
        wikiScraper.save(args.output_path)

if __name__=='__main__':
    main()