"""
File: WikiScraper.py
Author: Daniel Stancl

Description:
"""

# import libraries
import pandas as pd
import requests
from bs4 import BeautifulSoup


class WikiScraper(object):
    """
    """ 
    #####################
    ### MAGIC METHODS ###
    #####################
    def __init__(self):
        """
        """
        self.indexURL = {
            'S&P500': 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies',
            'FTSE100': 'https://en.wikipedia.org/wiki/FTSE_100_Index'
        }

        self.schema = ['Company', 'Symbol', 'Sector', 'ListedIn']

        self.data = pd.DataFrame(
            columns=self.schema
        )

    #####################
    ## PUBLIC METHODS ###
    #####################
    def scrape(self, stock_index):
        """
        A function that scrapes company names (and corresponding industries) listed in a given stock index.
        :param stock_index: name of stock index form WikiScraper.indexURL dict, type=str
            stock_index in ['S&P500', 'FTSE100']
        """
        assert stock_index in self.indexURL.keys(), "Param stock_index must be from a list ['S&P500', 'FTSE100']"
        self.stock_index = stock_index

        parsedHTML = self._getParsedHTML(stock_index)
        tableRows = self._getTableRows(parsedHTML)
        self.data = self.data.append(
            pd.DataFrame(self._parseRow(row) for row in tableRows)
        ).reset_index(drop=True)
        

    #####################
    ## PRIVATE METHODS ##
    #####################
    def _getParsedHTML(self, stock_index):
        """
        :param stock_index:
        """
        websiteHTML = requests.get(self.indexURL[stock_index]).text
        parsedWebsiteHTML = BeautifulSoup(websiteHTML, 'lxml')
        return parsedWebsiteHTML
    
    def _getTableRows(self, parsedHTML):
        """
        :param parsedHTML:
        """
        if self.stock_index == 'S&P500':
            table = parsedHTML.find('table', {'class': 'wikitable sortable'})
        elif self.stock_index == 'FTSE100':
            table = parsedHTML.findAll('table', {'class': 'wikitable sortable'})[1]
        
        return table.findAll('tr')[1:] # very first row contains columns names
    
    def _parseRow(self, row):
        """
        :param row:
        """
        if self.stock_index == 'S&P500':
            return pd.Series(
                {
                    'Company': row.findAll('a')[1].text,
                    'Symbol': row.findAll('a')[0].text,
                    'Sector': row.findAll('td')[3].text,
                    'ListedIn': self.stock_index
                }
            )

        elif self.stock_index == 'FTSE100':
            return pd.Series(
                {
                    'Company': row.findAll('td')[0].text,
                    'Symbol': row.findAll('td')[1].text,
                    'Sector': row.findAll('td')[2].text.strip('\n'),
                    'ListedIn': self.stock_index
                }
            )


wikiScraper = WikiScraper()
wikiScraper.scrape('S&P500') 
wikiScraper.scrape('FTSE100')

wikiScraper.data.Sector