"""
File: WikiScraper.py
Author: Daniel Stancl

Description:
"""
# parameters
stock_indices = ['S&P 500', 'FTSE 100', 'EURO STOXX 50']
db_path = '/mnt/c/Data/UCL/@MSc Project/DB/mysite/db.sqlite3'

# import libraries
import time
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3

class WikiScraper(object):
    """
    """ 
    #####################
    ### MAGIC METHODS ###
    #####################
    def __init__(self, db_path=db_path):
        """
        """
        self.indexURL = {
            'S&P 500': 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies',
            'FTSE 100': 'https://en.wikipedia.org/wiki/FTSE_100_Index',
            'EURO STOXX 50': 'https://en.wikipedia.org/wiki/EURO_STOXX_50'
        }

        # initialize the connection to the db
        self.conn = sqlite3.connect(db_path)
        self.curs = self.conn.cursor()

    #####################
    ## PUBLIC METHODS ###
    #####################
    def scrapeWikipedia(self, stock_index):
        """
        A function that scrapes company names (and corresponding industries) listed in a given stock index.
        :param stock_index: name of stock index form WikiScraper.indexURL dict, type=str
            stock_index in ['S&P500', 'FTSE100', 'EURO STOXX 50']
        """
        assert stock_index in self.indexURL.keys(), "Param stock_index must be from a list ['S&P500', 'FTSE100', 'EURO STOXX 50']"
        self.stock_index = stock_index

        parsedHTML = self._getParsedHTML(stock_index)
        tableRows = self._getTableRows(parsedHTML)
        self.data = self.data.append(
            pd.DataFrame(self._parseRow(row) for row in tableRows)
        ).reset_index(drop=True)

    def scrapeYahooFinance(self):
        """
        A function that scrapes some other company information from Yahoo Finance.
        At this moment, it is expected scrapeWikipedia function is utilized a priori, hence the assert condition.
        """
        assert self.data.shaoe[0] > 0, "Please, run self.scrapeWikipedia() first!"
        for i, companySymbol in enumerate(self.data.Symbol):
            self.data.loc[i, ['Sector', 'Industry', 'Country', 'Employees']] = self._getCompanyProfile(companySymbol)
            time.sleep(0.5)
            self.data.loc[i, 'Revenue'] = self._getCompanyRevenue(companySymbol)
            time.sleep(2)

    #####################
    ## PRIVATE METHODS ##
    #####################
    def _getCompanyCountry(self, profileContent):
        """
        :param profileContent:
        """
        try:
            return re.findall(r'<!-- react-text: (\d{1,2}) -->(.+?)<!-- /react-text -->', profileContent)[2][1] #country is third react text
        except:
            return str(None)
    
    def _getCompanyEmployees(self, profileContent):
        """
        :param profileContent:
        """
        try:
            return int(re.sub(',', '', profileContent.findAll('span')[-1].text))
        except:
            return 0

    def _getCompanyIndustry(self, profileContent):
        """
        :param profileContent
        """
        try:
            return profileContent.findAll('span')[-2].text
        except:
            return str(None)
    
    def _getCompanyProfile(self, symbol):
        """
        """
        url = f'https://finance.yahoo.com/quote/{symbol}/profile?p={symbol}'
        websiteHTML = requests.get(url).text
        parsedHTML = BeautifulSoup(websiteHTML, 'lxml')
        profileContent = str(parsedHTML.find('div', {'class': 'Mb(25px)'}))

        return pd.Series(
            {
                'Sector': self._getCompanySector(profileContent),
                'Industry': self._getCompanyIndustry(profileContent),
                'Country': self._getCompanyCountry(profileContent),
                'Employees': self._getCompanyEmployees(profileContent)
            }
        )

    def _getCompanyRevenue(self, symbol):
        """
        """
        url = f'https://finance.yahoo.com/quote/{symbol}/financials?p={symbol}'
        websiteHTML = requests.get(url).text
        parsedHTML = BeautifulSoup(websiteHTML, 'lxml')
        return 12
    
    def _getCompanySector(self, profileContent):
        """
        :param profileContent
        """
        try:
            return profileContent.findAll('span')[-3].text
        except:
            return str(None)    
    
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
        if self.stock_index == 'S&P 500':
            table = parsedHTML.find('table', {'class': 'wikitable sortable'})
        elif self.stock_index in ['FTSE 100', 'EURO STOXX 50']:
            table = parsedHTML.findAll('table', {'class': 'wikitable sortable'})[1]
        
        return table.findAll('tr')[1:] # very first row contains columns names
    
    def _parseRow(self, row):
        """
        :param row:
        """
        if self.stock_index == 'S&P 500':
            return pd.Series(
                {
                    'Company': row.findAll('a')[1].text,
                    'Symbol': row.findAll('a')[0].text,
                    'ListedOn': self.stock_index
                }
            )

        elif self.stock_index == 'FTSE  100':
            return pd.Series(
                {
                    'Company': row.findAll('td')[0].text,
                    'Symbol': row.findAll('td')[1].text,
                    'ListedOn': self.stock_index
                }
            )
        
        elif self.stock_index == 'EURO STOXX 50':
            return pd.Series(
                {
                    'Company': row.findAll('a')[2].text,
                    'Symbol': row.findAll('td')[0].text,
                    'ListedOn': self.stock_index
                }
            )
    
    
    
#######################
##### APPLICATION #####
#######################
"""
wikiScraper = WikiScraper()
for stock_index in stock_indices:
    wikiScraper.scrapeWikipedia(stock_index)
wikiScraper.data


websiteHTML = requests.get(self.indexURL[stock_index]).text
parsedWebsiteHTML = BeautifulSoup(websiteHTML, 'lxml')

url = 'https://finance.yahoo.com/quote/ADS.DE/financials?p=ADS.DE'
html = requests.get(url).text
parsedHTML = BeautifulSoup(html, 'lxml')
text = parsedHTML.find('div', {'class': 'Mb(25px)'})
str_text = str(text)

text.findAll('span')[-1].text

re.findall(r'<!-- react-text: (\d{1,2}) -->(.+?)<!-- /react-text -->', str_text)[2][1]
"""