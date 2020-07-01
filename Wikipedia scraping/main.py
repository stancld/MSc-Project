# setup
import os
import sys
from argparse import ArgumentParser
from WikiScraper import *
from set_django_db import set_django_db

# parameters/arguments
parser = ArgumentParser()

parser.add_argument(
    '--stock_indices',
    default=['S&P 500', 'FTSE 100', 'EURO STOXX 50'],
    help="A list of stock indices that should be scraped.\
        Currently supported: `['S&P 500', 'FTSE 100', 'EURO STOXX 50']`."
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
if (args.mysite_path) & (args.output_path):
    raise Exception(
        'mysite_path!=None and output_path!=None is not compatible\
            because output_path is used iff mysite_path=None.'
    )
if (not args.mysite_path) & (not args.output_path):
    raise Exception(
        'mysite_path==None and output_path==None is not compatible\
            because output_path has no default value while must be specified.'
    )

#######################
##### APPLICATION #####
#######################
def main(): 
    if args.mysite_path :
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