# setup
import os
import sys
from django.utils import timezone
from WikiScraper import *

if __name__=='__main__':
    # import Company - django.db.models.Model
    exec(open('set_django_db.py').read())
    from tables_daniel.models import Company

    # parameters
    stock_indices = ['S&P 500', 'FTSE 100', 'EURO STOXX 50']
    stock_indices = ['EURO STOXX 50']

    #######################
    ##### APPLICATION #####
    #######################
    wikiScraper = WikiScraper(CompanyWriter=Company)
    for stock_index in stock_indices:
        wikiScraper.scrapeWikipedia(stock_index)
    wikiScraper.scrapeYahooFinance()
    wikiScraper.writeToDjangoDB()