"""
File: WikiScraper.py
Author: Daniel Stancl

Description: Class WikiYahooScraper used for MSc Project.
"""

# import libraries
import time
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import django
from django.utils import timezone

class WikiScraper(object):
    """
    More proper name of this class is WikiYahooScraper.
    This class has two major purposes:
        1. It is capable to scrape companies listed on some major stock indices from Wikipedia.
        2. It is able to find more information for companies obtained in the step 1 from Yahoo Finance.
    Subsequently, this class can save the data either as csv/xlsx file using pandas, or the data can be sent to django dataabse.
    """ 
    #####################
    ### MAGIC METHODS ###
    #####################
    def __init__(self, CompanyWriter=None):
        """
        :param CompanyWriter:
            CompanyWriter is django Model base that is used for writing and storing the data in a given databse
            type=django.db.models.base.ModelBase
        """
        self.indexURL = {
            'S&P 500': 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies',
            'FTSE 100': 'https://en.wikipedia.org/wiki/FTSE_100_Index',
            'EURO STOXX 50': 'https://en.wikipedia.org/wiki/EURO_STOXX_50'
        }

        self.schema = [
            'CompanyID', 'Company', 'Symbol',
            'ListedOn', 'Sector', 'Industry',
            'Country', 'NoEmployees', 'Revenue',
            'Timestamp']
        self.data = []

        if CompanyWriter == None:
            # if no database is attached, pandas DataFrame are used instead
            self.CompanyWriterIsUsed = False
        else:
            # in othercase, CompanyWriter is stored
            assert type(CompanyWriter) == django.db.models.base.ModelBase, 'param CompanyWritert must be of type django.db.models.base.ModelBase!'
            self.CompanyWriter = CompanyWriter
            self.CompanyWriterIsUsed = True

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

        parsedHTML = self._getParseWikiHTML(stock_index)
        tableRows = self._getTableRows(parsedHTML)
        
        self.data.extend(
            [self._parseWikiTableRow(row) for row in tableRows]
        )

    def scrapeYahooFinance(self):
        """
        A function that scrapes some other company information from Yahoo Finance.
        At this moment, it is expected scrapeWikipedia function is utilized a priori, hence the assert condition.
        """
        assert len(self.data) > 0, "Please, run self.scrapeWikipedia() first!"
        for i, dataRow in enumerate(self.data):
            self.data[i].update(
                self._getCompanyProfile(dataRow['Symbol'])
            )
            time.sleep(2.5)
            self.data[i].update(
                self._getCompanyRevenue(dataRow['Symbol'])
            )
            time.sleep(2.5)
            self.data[i].update(
                {
                    'CompanyID': i, # can be substituted by more elaborated ticker in the future
                    'Timestamp': timezone.now()
                }
            )
            
            if (i+1)%20==0:
                print(f'{i+1:.0f} companies out of {len(self.data):.0f} scraped from Yahoo.')

    def saveToCSV(self, path):
        """
        Function saving the scraped data into a csv file.
        :param path: absolute path of a stored file; type=str
        """
        if self.CompanyWriterIsUsed:
            print('Alert: CompanyWriter is defined. Would you like to store the data in djnago database instead?')
        
        pd.DataFrame(
            self.data,
	        columns=self.schema
        ).to_csv(path)

    def saveToExcel(self, path):
        """
        Function saving the scraped data into a xlsx file.
        :param path: absolute path of a stored file; type=str
        """
        if self.CompanyWriterIsUsed:
            print('Alert: CompanyWriter is defined. Would you like to store the data in djnago database instead?')
        
        pd.DataFrame(
            self.data,
	        columns=self.schema
        ).to_excel(path)

    def writeToDjangoDB(self):
        """
        Function writing the scraped dat into an existing django database.
        """
        [self._writeRowToDjangoDB(datarow) for datarow in self.data]

    #####################
    ## PRIVATE METHODS ##
    #####################
    def _getCompanyCountry(self, profileContent):
        """
        This function gets country of company's HQ from Yahoo Finance.
        Parsing company's country is a bit tricky as it an be located whenever from 1st to 4th row in the react text.
        :param profileContent: content of profile section from Yahoo Finance in string format; type=str
        """
        try:
            i = 0
            location = re.findall(r'<!-- react-text: (\d{1,2}) -->(.+?)<!-- /react-text -->', profileContent)[i][1] 
            while ( any( type(self._transformToInt(x))==int for x in re.split(' |-', location) ) ) & ( i<3 ):
                i+=1
                try:
                    location = re.findall(r'<!-- react-text: (\d{1,2}) -->(.+?)<!-- /react-text -->', profileContent)[i][1] 
                except:
                    pass
            return location
        except:
            return str(None)
    
    def _getCompanyEmployees(self, profileContent):
        """
        This function gets a number of comapny's employees Yahoo Finance.
        :param profileContent: content of profile section from Yahoo Finance in string format; type=str
        """
        try:
            return int(re.sub(',', '', re.findall(r'<span data-reactid="(\d{1,2})">(.+?)</span>', profileContent)[-1][1]))
        except:
            return 0

    def _getCompanyIndustry(self, profileContent):
        """
        This function gets an industry a company operates in from Yahoo Finance.
        :param profileContent: content of profile section from Yahoo Finance in string format; type=str
        """
        try:
            return re.findall(r'data-reactid="(\d{1,2})">(.+?)</span>', profileContent)[-3][1]
        except:
            return str(None)
    
    def _getCompanyProfile(self, symbol):
        """
        Within this function, Yahoo HTML is parsed and a company's Sector, Industry, Conytr of HQ and number of employees are returned.
        While & try/except loop is required as sometimes an access to webpage might be denied.
        :param symbol: stock symbol of a company that is used for completing url address on Yahoo Finance; type=str
        """
        isSuccess, fails = False, 0
        while (isSuccess == False) & (fails < 20):
            try:
                parsedHTML = self._getParseYahooHTML(symbol, 'profile')
                isSuccess = True
            except:
                fails+=1
                if fails % 5 == 0:
                    time.sleep(60)
                else:
                    time.sleep(1)
        profileContent = str(parsedHTML.find('div', {'class': 'Mb(25px)'}))
        
        return {
            'Sector': self._getCompanySector(profileContent),
            'Industry': self._getCompanyIndustry(profileContent),
            'Country': self._getCompanyCountry(profileContent),
            'NoEmployees': self._getCompanyEmployees(profileContent)
        }

    def _getCompanyRevenue(self, symbol):
        """
        This function resemlbes a simplified combination of self._getCompanyProfile and one of self._getCompanyEmployees etc.
        While & try/except loop is required as sometimes an access to webpage might be denied.
        :param symbol: stock symbol of a company that is used for completing url address on Yahoo Finance; type=str
        """
        isSuccess, fails = False, 0
        while (isSuccess == False) & (fails < 20):
            try:
                parsedHTML = self._getParseYahooHTML(symbol, 'financials')
                isSuccess = True
            except:
                fails+=1
                if fails % 5 == 0:
                    time.sleep(60)
                else:
                    time.sleep(1)
        try:
            revenue = self._parseRevenue(parsedHTML)
            return {'Revenue': revenue}
        except:
            return {'Revenue': 0}
        
    
    def _getCompanySector(self, profileContent):
        """
        This function gets an industry a company operates in from Yahoo Finance.
        :param profileContent: content of profile section from Yahoo Finance in string format; type=str
        """
        try:
            return re.findall(r'data-reactid="(\d{1,2})">(.+?)</span>', profileContent)[-5][1]
        except:
            return str(None)    
    
    def _getParseYahooHTML(self, symbol, content):
        """
        This function parses Yahoo HTML content subsequenlty used in _getCompanyProfile & _getCompanyRevenue functions.
        :param symbol: stock symbol of a company that is used for completing url address on Yahoo Finance; type=str
        :param content: an indication which 
            supported values: ['profile', financials]
        """
        assert content in ['profile', 'financials'], "Param content must be drawn from ['profile', 'financials']."
        url = f'https://finance.yahoo.com/quote/{symbol}/{content}?p={symbol}'
        websiteHTML = requests.get(url).text
        parsedHTML = BeautifulSoup(websiteHTML, 'lxml')
        return parsedHTML

    def _getParseWikiHTML(self, stock_index):
        """
        This function parses wikipedia HTML into machine-readable format used in other function.
        The specific parsing is chocen based upon the stock_index param.
        :param stock_index: stock_index; type=str
        """
        websiteHTML = requests.get(self.indexURL[stock_index]).text
        parsedWebsiteHTML = BeautifulSoup(websiteHTML, 'lxml')
        return parsedWebsiteHTML
    
    def _getTableRows(self, parsedHTML):
        """
        This function gets the whole table (splitted into individual rows) from Wikipedia page.
        :param parsedHTML: parsed webiste returned by _getParseWikiHTML function; type=bs4
        """
        if self.stock_index == 'S&P 500':
            table = parsedHTML.find('table', {'class': 'wikitable sortable'})
        elif self.stock_index in ['FTSE 100', 'EURO STOXX 50']:
            table = parsedHTML.findAll('table', {'class': 'wikitable sortable'})[1]
        
        return table.findAll('tr')[1:] # very first row contains columns names
    
    def _parseRevenue(self, parsedHTML):
        """
        Parsing company's revenue from the table posted on Yahoo Finance is not straightforward hence a single function is dedicated to this task.
        :param parsedHTML: parsed webiste returned by _getParseYahooHTML function; type=bs4
        """
        financialTable = parsedHTML.find('div', {'class': 'D(tbrg)'})
        unparsedRevenue = str(financialTable.find_all('div', {'class': 'Ta(c) Py(6px) Bxz(bb) BdB Bdc($seperatorColor) Miw(120px) Miw(140px)--pnclg Bgc($lv1BgColor) fi-row:h_Bgc($hoverBgColor) D(tbc)'})[0])
        revenue = int(re.sub(
            ',', '', re.findall(r'<span data-reactid="(\d{1,2})">(.+?)</span>', unparsedRevenue)[0][1]
        ))
        return revenue
    
    def _parseWikiTableRow(self, row):
        """
        This function parses an individual row from Wiki Table returned by _getTableRows function.
        :param row: a single row from a Wiki table; type=bs4
        """
        if self.stock_index == 'S&P 500':
            return {
                'Company': row.findAll('a')[1].text,
                'Symbol': row.findAll('a')[0].text,
                'ListedOn': self.stock_index
            }
            
        elif self.stock_index == 'FTSE 100':
            return {
                'Company': row.findAll('td')[0].text,
                'Symbol': row.findAll('td')[1].text,
                'ListedOn': self.stock_index
            }
        
        elif self.stock_index == 'EURO STOXX 50':
            return {
                'Company': row.findAll('a')[2].text,
                'Symbol': row.findAll('td')[0].text,
                'ListedOn': self.stock_index
            }
    
    def _writeRowToDjangoDB(self, datarow):
        """
        This function writes the scraped records into a connected django database.
        :param datarow: datarow is a single dict element from the list of all scraped records; type=dict
        """
        try:
            companyRecord = self.CompanyWriter(
                CompanyID = datarow['CompanyID'],
                Company = datarow['Company'],
                Symbol = datarow['Symbol'],
                ListedOn = datarow['ListedOn'],
                Sector = datarow['Sector'],
                Industry = datarow['Industry'],
                Country = datarow['Country'],
                NoEmployees = datarow['NoEmployees'],
                Revenue = datarow['Revenue'],
                Timestamp = datarow['Timestamp']
            )
            companyRecord.save()
        except Exception as e:
            print(e)

    def _transformToInt(self, x):
        """
        This helper function transforms a given str element to int if possible, otherwise str element is returned.
        :param x: an address element from YahooFinance profile section; type=str
        """
        try:
            return int(x.strip().strip(','))
        except:
            return x.strip().strip(',')