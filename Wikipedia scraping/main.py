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
        Currently supported are: `['S&P 500', 'FTSE 100', 'EURO STOXX 50']`."
)

parser.add_argument(
    '--use_django_db',
    default=True,
    help='An indication whether scraped data should be stored at django DB.\
        If `False` is passed, the data are stored as a csv/xlsx file. '
)

parser.add_argument(
    '--mysite_path',
    default='/mnt/c/Data/UCL/@MSc Project/DB/mysite/',
    help='An absolute path to a Django app.'
)

parser.add_argument(
    '--output_path',
    default=None,
    help='A path of an output file if `use_django_db==False`'
)

args = parser.parse_args()

# sanity checks
if (args.use_django_db) & (args.output_path != None):
    raise Exception(
        'use_django_db=True and output_path!=None is not compatible\
            because output_path is used iff use_django_db=False.'
    )
if (not args.use_django_db) & (args.output_path == None):
    raise Exception(
        'use_django_db=False and output_path==None is not compatible\
            because output_path has no default value while must be specified.'
    )

#######################
##### APPLICATION #####
#######################
def main(): 
    if args.use_django_db == True:
        # import Company - django.db.models.Model
        set_django_db(mysite_path=args.mysite_path)
        from tables_daniel.models import Company

        wikiScraper = WikiScraper(CompanyWriter=Company)
    else:
        wikiScraper = WikiScraper()

    for stock_index in args.stock_indices:
        wikiScraper.scrapeWikipedia(stock_index)
    wikiScraper.scrapeYahooFinance()
    
    if args.use_django_db == True:
        wikiScraper.writeToDjangoDB()
    else:
        wikiScraper.save(args.output_path)

if __name__=='__main__':
    main()