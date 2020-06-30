# setup
from WikiScraper import *

# parameters
stock_indices = ['S&P 500', 'FTSE 100', 'EURO STOXX 50']

#######################
##### APPLICATION #####
#######################
wikiScraper = WikiScraper()
for stock_index in stock_indices:
    wikiScraper.scrapeWikipedia(stock_index)
wikiScraper.scrapeYahooFinance()
wikiScraper.data.to_excel('/mnt/c/Data/firms.xlsx')