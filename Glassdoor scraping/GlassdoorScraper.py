"""
File: GlassdoorScraper.py
Author: Daniel Stancl
"""

# import libraries
import time
import datetime
from datetime import date
import re
import numpy as np
import pandas as pd
import django
import json
from django.utils import timezone
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

## CLASS
class GlassdoorScraper(object):
    """
    The major purpose of this class is to scrape reviews from Glassdoor.
    As such, all actions which are necessary during the browsing of the web are defined throughout this class.
    Subsequently, this class can save the data either as csv/xlsx file using pandas, or the data can be sent to django dataabse.
    """
    #####################
    ### MAGIC METHODS ###
    #####################

    def __init__(self, chrome_driver_path, email, password, headless_browsing,
                review_writer, company_reader, max_review_age, min_date):
        """
        Instantiate method handling all the necessary setting.

        :param path_chrome_drive: An absolute path to a ChromeDriver.
        :param email: Email used for log in to the Glassdoor account; type=str
        :param password: Password used for log in to the Glassdoor account; type=str
        :param headless_browsing: If True, `headless` browsing is to be used.
        :param review_writer:
            This django Model base that is used for writing and storing the data in a given database;
            type=django.db.models.base.ModelBase
        :param company_reader:
            This django Model base that is used for reading the data from a given database;
            type=django.db.models.base.ModelBase
        :param max_review_age: An indication how old reviews are to be scraped; type=int|float
        :param min_date: An indication up to which date reviews are to be scraped.; type=str
        """
        # configure driver & ChromeOptions
        self.chrome_driver_path=chrome_driver_path
        self.headless_browsing = headless_browsing
        
        self.chrome_options = webdriver.ChromeOptions()
        
        self.chrome_options.add_argument('--ignore-certificate-errors')
        self.chrome_options.add_argument('--ignore-certificate-errors-spki-list')
        self.chrome_options.add_argument('--ignore-ssl-errors')
        
        if headless_browsing:
            self.chrome_options.add_argument('--headless')
            self.chrome_options.add_argument('--log-level=3')
            self.chrome_options.add_argument('--silent') # --log-level=3 & --silent disable logging
            self.chrome_options.add_argument('--disable-gpu')
            self.chrome_options.add_argument("--no-sandbox")
            self.chrome_options.add_argument('window-size=1440,1080')
            self.chrome_options.add_argument('--enable-features=AllowSyncXHRInPageDismissal')
        
        self.driver = webdriver.Chrome(
            executable_path=chrome_driver_path,
            options=self.chrome_options
        )

        if (not headless_browsing):
            self.driver.set_window_size(1440, 1080)
            self.driver.set_window_position(0,0)
        
        # store url to the glassdor reviews main page
        self.url = 'https://www.glassdoor.com/Reviews/index.htm'
        # store email & password
        self.email = email
        self.password = password

        # Instantiate empty dataframe for storing reviews
        self.schema = [
            'Company', 'ReviewTitle', 'Year',
            'Month', 'Day', 'Rating',
            'JobTitle', 'Location', 'Recommendation',
            'Outlook', 'OpinionOfCEO', 'Contract',
            'ContractPeriod', 'Pros', 'Cons',
            'AdviceToManagement', 'Timestamp'
        ]
        self.data = []

        # a dictionary for converting three-letter months into an integer
        self.monthToInt = {
            'Jan': 1, 'Feb': 2, 'Mar': 3,
            'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9,
            'Oct': 10, 'Nov': 11, 'Dec': 12
        }   

        # get current date so that scraping can be stop w.r.t. date
        self.current_date = date.today()
        self.no_min_date = datetime.datetime.strptime("1800-01-01",'%Y-%m-%d')
        if min_date:
            self.min_date = datetime.datetime.strptime(min_date, '%Y-%m-%d')
            self.max_review_age = float(np.inf)
        elif max_review_age:
            self.max_review_age = max_review_age # how old reviews might be
            self.min_date = self.no_min_date
        else:
            self.min_date = self.no_min_date
            self.max_review_age = float(np.inf)

        # sanity checks
        assert type(email)==str, 'Param email must be a type of str'

        if review_writer:
            assert type(review_writer) == django.db.models.base.ModelBase, 'param review_writer must be of type django.db.models.base.ModelBase!'
            assert type(company_reader) == django.db.models.base.ModelBase, 'param company_reader must be of type django.db.models.base.ModelBase!'
            self.ReviewWriter = review_writer
            self.CompanyReader = company_reader
            self.reviewWriterIsUsed = True
        else:
            self.data_to_save = []

    ######################
    ### PUBLIC METHODS ###
    ## major func first ##
    # alphabetical order #
    ######################

    def scrape(self, company_name, location, 
                limit = float(np.inf)):
        """
        MAIN FUNCTION
        This function is applied once a driver is signed in to the Glassdoor portal using self.GetOnReviewsPage function.

        :param company_name: company name; type=str
        :param location: city; type=str
        :param limit: a number of pages to be scraped; type=int
        """
        if self.reviewWriterIsUsed:
            # make self.data to be always an empty list if they are to be written into django db
            self.data = []
        
        # store company_name and filter out the company from CompanyDB
        self.company_name = company_name # store company_name
        self.company_django = self.CompanyReader.objects.get(Company=self.company_name)
    
        scraping_startTime = time.time()
        print(f"{self.company_name} is being scraped.")
        while (self.page <= limit) & (self._isNextPageAvailable()) & ( (self._newerThanGivenYears()) | (self._newerThanMinDate()) ):
            try:
                self._clickContinueReading()
                self.getReviews()           
                self.data.extend(
                    [self.parseReview(review) for review in self.reviews]
                )
            except:
                pass
            self._goNextPage()

            # save some intermediate files
            if (self.page-1) % 50==0:
                if self.reviewWriterIsUsed:
                    [self._writeRowToDjangoDB(datarow) for datarow in self.data]
                    self.data = []
                    print(
                        f"Part of reviews for {self.company_name} has been scraped and stored."
                    )       
                else:
                    self.data_to_save.extend(self.data)
            
            # print the state
            t = time.time() - scraping_startTime
            print(
                f"Page {self.page} reached after {t:.2f} seconds."
            )
            
        print(
            f"Reviews for {self.company_name} has been scraped and stored."
        )
        
        # store the data if they are to be stored in django DB
        
        if self.reviewWriterIsUsed:
            [self._writeRowToDjangoDB(datarow) for datarow in self.data]
        else:
            self.data_to_save.extend(self.data)

    def acceptCookies(self):
        """
        Accept cookies consent if displayed.
        This is important as a given bar hides important stuff.
        """
        try:
            self.driver.find_element_by_id('onetrust-accept-btn-handler').click()
        except:
            print('No cookies consent is required to accept.')
    
    def getOnReviewsPage(self, company_name, location, url):
        """
        Function that is responsible for log in to the Glassdoor account.
        Subsequently, it gets a driver on the first page of reviews for a given company.
        Eventually, it sorts reviews from the most recent
        :param company_name: company name; type=str
        :param location: city; type=str
        """
        self._signIn()
        time.sleep(2)

        self.company_name = company_name
        
        if url:
            self.getURL(url)
            if 'sort.sortType=RD&sort.ascending=false' not in self.driver.current_url: # sort reviews if they are not according to the url address
                self._sortReviewsMostRecent()
            if self._isLoginRequiredWhite():
                self._signInWhite()

        else:
            success, fails = 0, 0
            while (success==0) & (fails < 5):
                self.getURL(self.url)
                self.searchReviews(company_name, location)
                time.sleep(3)
                if self._isNotUniqueSearchResult():
                    print('First company from the list selected.')
                    self._selectFirstCompany()
                    print(self.page)
                try:
                    self._clickReviewsButton()
                    time.sleep(2)

                    self._sortReviewsMostRecent()
                    success += 1
                except:
                    fails += 1
                    print(f'The attempt no.{fails} to get on reviews page fails.')
                    time.sleep(120)
        self.page = 1
        
    def getURL(self, url):
        """
        Get on URL and then sleep for a while to make sure web content to be loaded properly.
        :param url: url; type=str
        """
        self.driver.get(url)
        time.sleep(1)
    
    def getReviews(self):
        """
        A function returning a list of WebElements corresponding to individual  reviews displayed on a given page.
        There are two classes of empReview hence must be collected in two steps.
        *It might be moved to private functions*
        """
        self.reviews = self.driver.find_elements_by_xpath('//li[@class="empReview cf"]')
        self.reviews.extend(self.driver.find_elements_by_xpath('//li[@class="noBorder empReview cf"]'))    
   
    def saveToCSV(self, path):
        """
        Function saving the scraped data to a csv file.
        :param path: path of output csv file; type=str
        """
        if self.reviewWriterIsUsed == True:
            print(f'Data cannot be saved to {path} as they have continuosly pushed to django database.')
        pd.DataFrame(
            self.data_to_save,
            columns=self.schema
        ).to_csv(path)

    def saveToExcel(self, path):
        """
        Function saving the scraped data to a xlsx file.
        :param path: path of output xlsx file; type=str
        """
        if self.reviewWriterIsUsed == True:
            print(f'Data cannot be saved to {path} as they have continuosly pushed to django database.')
        pd.DataFrame(
            self.data_to_save,
            columns=self.schema
        ).to_excel(path)
    
    def searchReviews(self, company_name, location):
        """
        A function that is responsible for searching company's reviews once a driver is on a main review page.
        *It might be moved to private functions*
        :param company_name: company name; type=str
        :param location: city; type=str
        """
        if len(company_name.split()) > 2:
            company_name_to_search = ' '.join(company_name.split()[:2])
        else:
            company_name_to_search = company_name
        try:
            self._fillCompanyName(company_name_to_search)
            self._fillLocation(location)
            self._clickSearchButton()
        except:
            self._fillCompanyNameSecondary(company_name_to_search)
            self._fillLocationSecondary(location)
            self._closeAddResumeWindow()
            self._clickSearchButtonSecondary()
        time.sleep(1)
    
    def parseReview(self, review):
        """
        Parse a whole single review into individual elements listed below according to self.schema.
        :param review: WebElement
        """
        self._getReviewHTML(review) # create self.reviewHTML object
        self._parseReviewElements()
        
        return {
            'Company': self.company_django,
            'ReviewTitle': self._getReviewTitle(),
            'Year': self._getTimestamp(element='Year'),
            'Month': self._getTimestamp(element='Month'),
            'Day': self._getTimestamp(element='Day'),
            'Rating': self._getRating(),
            'JobTitle': self._getJobTitle(),
            'EmployeeRelationship': self._getEmployeeRelationship(),
            'Location': self._getLocation(),
            'Recommendation': self._getRecommendationBar(element='Recommendation'),
            'Outlook': self._getRecommendationBar(element='Outlook'),
            'OpinionOfCEO': self._getRecommendationBar(element='OpinionOfCEO'),
            'Contract': self._getContract(),
            'ContractPeriod': self._getContractPeriod(),
            'Pros': self._getReviewBody(element='Pros'),
            'Cons': self._getReviewBody(element='Cons'),
            'AdviceToManagement': self._getReviewBody(element='Advice to Management'),
            'Timestamp': timezone.now()
        }
    
    #######################
    ### PRIVATE METHODS ###
    ## alphabetical order #
    #######################

    def _clickContinueReading(self):
        """
        Click "Continue reading" button to unroll the whole version of reviews.
        """
        while len(self._getContinueReadingList()) > 0:
            continueReadingPresent = 0
            attempts = 0
            while (continueReadingPresent == 0) & (attempts < 15):
                try:
                    self._getContinueReadingList()[0].click()
                    continueReadingPresent += 1
                except:
                    attempts += 1
                    time.sleep(1)
            if attempts == 15:
                self.getURL(self.driver.current_url) # refresh page if access is denied
            time.sleep(np.random.uniform(1.5, 2.5))
    
    def _clickReviewsButton(self):
        """
        Click "Reviews" button on a company's profile to dislay the first review page.
        """
        self.driver.find_element_by_xpath('//*[@id="EIProductHeaders"]/div/a[1]').click()

    def _clickSearchButton(self):
        """
        Click "Search" button to trigger search for a company's profile.
        """
        self.driver.find_element_by_class_name("gd-btn-mkt").click()
    
    def _clickSearchButtonSecondary(self):
        """
        Click "Search" button to trigger search for a company's profile.
        """
        try:
            self.driver.find_element_by_xpath('/html/body/div[7]/div/nav[1]/div/div/div/div[4]/div[3]/form/div/button').click()
        except:
            self.driver.find_element_by_xpath('/html/body/div[6]/div/nav[1]/div/div/div/div[4]/div[3]/form/div/button').click()

    def _closeAddResumeWindow(self):
        """
        Functionality closing 'Add resume' to complete the Glassdoor profile, as it hides 'search button'
        """
        try:
            self.driver.find_element_by_class_name('SVGInline-svg').click()
        except:
            pass

    def _fillCompanyName(self, company_name):
        """
        Fill a company name in a search field on the title page.
        :param company_name: company name; type=str
        """
        assert type(company_name) == str, 'Param company_name must be a type of str.'
        self.driver.find_element_by_class_name("keyword").clear()
        self.driver.find_element_by_class_name("keyword").send_keys(company_name)

    def _fillCompanyNameSecondary(self, company_name):
        """
        Fill a company name in a search field on the title page if a different page is displayed.
        :param company_name: company name; type=str
        """
        assert type(company_name) == str, 'Param company_name must be a type of str.'
        self.driver.find_element_by_id("sc.keyword").clear()
        self.driver.find_element_by_id("sc.keyword").send_keys(company_name)

    def _fillLocation(self, location):
        """
        Fill a company name in a search field on the title page.
        :param location: city; type=str
        """
        assert type(location) == str, 'Param locaation must be a type of str.'
        self.driver.find_element_by_class_name("loc").clear()
        self.driver.find_element_by_class_name("loc").send_keys(location)

    def _fillLocationSecondary(self, location):
        """
        Fill a company name in a search field on the title page if a different page is displayed..
        :param location: city; type=str
        """
        assert type(location) == str, 'Param locaation must be a type of str.'
        self.driver.find_element_by_id("sc.location").clear()
        self.driver.find_element_by_id("sc.location").send_keys(location)

    def _getEmployeeRelationship(self):
        """
        Parse reviewer's employee relationship, i.e. a former or current one, from review-HTML if available. 
        """
        try:
            titleAndRelationshop = re.search('<span class="authorJobTitle middle">(.+?)</span>', self.reviewHTML).group(1)
            return titleAndRelationshop.split(' - ')[1]
        except:
            return ''
    
    def _getContinueReadingList(self):
        """
        Get the most recent version of 'Continue reading' buttons on reviews page. These are then clickable
        """
        return self.driver.find_elements_by_xpath(
            '//div[@class="v2__EIReviewDetailsV2__continueReading v2__EIReviewDetailsV2__clickable"]'
        )
    
    def _getContract(self):
        """
        Parse information whether a reviewer is/was a full-time/part-time employee.
        """
        try:
            return [word for word in self.mainText.split() if 'time' in word][0]
        except:
            return ''

    def _getContractPeriod(self):
        """
        Parse information how long a reviewr was/has been working for a company.
        """
        try:
            return re.search('for (.+)', self.mainText).group(1)
        except:
            return ''
    
    def _getJobTitle(self):
        """
        Parse reviewer's job title from review-HTML if available.
        """
        try:
            titleAndRelationshop = re.search('<span class="authorJobTitle middle">(.+?)</span>', self.reviewHTML).group(1)
            return titleAndRelationshop.split(' - ')[0]
        except:
            return ''
    
    def _getLocation(self):
        """
        Parse reviewer's job location from review-HTML if available.
        """
        try:
            return re.search('<span class="authorLocation">(.+?)</span>', self.reviewHTML).group(1)
        except:
            return ''
    
    def _getRating(self):
        """
        Parse review rating from review-HTML if available.
        """
        try:
            return re.search('<div class="v2__EIReviewsRatingsStylesV2__ratingNum v2__EIReviewsRatingsStylesV2__small">(.+?)</div>', self.reviewHTML).group(1)
        except:
            return None

    def _getRecommendationBar(self, element):
        """
        Get a single element from a recomendation bar containing items/attributes like ('positive outlook', 'approves of CEO') etc.
        :param element: element to be parsed from recommendation bar; type=str
            Select from: ['Recommendation', 'Outlook', 'OpinionOfCEO']
        """
        assert type(element) == str, 'Param element must be a type of str.'
        assert element in ['Recommendation', 'Outlook', 'OpinionOfCEO'], "Element must be drawn from the list ['Recommendation', 'Outlook', 'OpinionOfCEO']."
        return self.recommendationBar[element]

    def _getReviewBody(self, element):
        """
        Get individual elements of the review body
        :param element: A string indicating a component of a review body; type=str
            select from: ['Pros', 'Cons', 'Advice to Management']
        """
        assert type(element) == str, 'Param element must be a type of str.'
        assert element in ['Pros', 'Cons', 'Advice to Management'], "Element must be drawn from the list ['Pros', 'Cons', 'Advice to Management']."
        try:
            return self.parsedReviewBody[element]
        except:
            return ''
    
    def _getReviewHTML(self, review):
        """
        Get attribute 'outerHTML' from a WebElement corresponding to a single review.
        :param review: WebElement
        """
        self.reviewHTML = review.get_attribute('outerHTML')

    def _getReviewTitle(self):
        """
        Parse review title from review-HTML if filled.
        """
        try:
            return re.search('reviewLink">"(.+?)"</a>', self.reviewHTML).group(1)
        except:
            return ''

    def _getTimestamp(self, element):
        """
        Get a single element = Day | Month | Year; from a timestamp.
        :param element: get a single element of a date, type=str
            select from: ['Day', 'Month', 'Year']
        """
        assert type(element) == str, 'Param element must be a type of str.'
        assert element in ['Day', 'Month', 'Year'], "Element must be drawn from the list ['Day', 'Month', 'Year']."
        if self.timestamp != 'Featured Review':
            if element == 'Day':
                return int(self.timestamp.split()[2])
            elif element == 'Month':
                return self.monthToInt[
                    self.timestamp.split()[1]
                ]
            elif element == 'Year':
                return int(self.timestamp.split()[3])
        else:
            return 0
    
    def _goNextPage(self):
        """
        A function that takes a driver to the next page.
        """
        if '_P' in self.driver.current_url:
            next_url = re.sub('_P(.+?).htm', f'_P{(self.page)+1}.htm', self.driver.current_url)
        else:
            next_url = re.sub('.htm', '_P2.htm', self.driver.current_url)
        self.getURL(next_url)
        self.page += 1
        time.sleep(2)

    def _haveDesiredDate(self, datarow):
        """
        A function that returns boolean whether a given reviews falls within a confined date range.
        """
        try:
            review_date = datetime.datetime.strptime(
                '-'.join(
                    [str(datarow['Year']), str(datarow['Month']), str(datarow['Day'])],
                ), '%Y-%m-%d'
            ).date()
            if review_date < min_date:
                return False
            else:
                return True
        except:
            return False


    def _isLoginRequired(self):
        """
        A function that checks if login is required.
        """
        return len(self.driver.find_elements_by_name('username')) > 0
    
    def _isLoginRequiredWhite(self):
        """
        A function that checks if login is required.
        """
        return len(self.driver.find_elements_by_xpath('/html/body/div[4]/div/div/div/div/div/div/div/div[2]/div/a')) > 0

    def _isNextPageAvailable(self):
        """
        The function finds out whether the next page contains any review and returns boolean if so or not.
        Sometimes access to the webpage may be denied hence we try to approach it multiple times with time.sleep.
        """
        self.getReviews()
        attempts = 0
        while (len(self.reviews) == 0) & (attempts < 3):
            self.getURL(self.driver.current_url)
            self.getReviews()
            time.sleep(20)
            attempts += 1

        return len(self.reviews) > 0

    def _isNotUniqueSearchResult(self):
        """
        It might happen a list of companies is returned when a company name is searched.
        This is an identifier of such an occasion.
        """
        return len(self.driver.find_elements_by_id('SearchResults')) != 0

    def _newerThanGivenYears(self):
        """
        A function that returns a boolean whether the oldest scraped review is less than given maximum age.
        Sometimes a featured review may occur, which disables to compute time_delta.
        Not to overcomplicate dropping these records during the scraping, we just look up to the first non-featured review
        through while and try&except loop.
        we 
        """
        if self.max_review_age != float(np.inf):
            if len(self.data) > 0:
                last_date = None
                t = 1
                while last_date == None:
                    try:
                        last_date = datetime.datetime.strptime(
                                '-'.join(
                                    [str(self.data[-t]['Year']), str(self.data[-t]['Month']), str(self.data[-t]['Day'])]
                                    ), '%Y-%m-%d'
                            ).date()
                        time_delta = (self.current_date - last_date).days / 365
                    except:
                        t += 1
                return time_delta < self.max_review_age
            else:
                return True
        else:
            return False # as it is not applied
    
    def _newerThanMinDate(self):
        """
        A function that returns a boolean whether the oldest scraped review has more recent date than min_date.
        Sometimes a featured review may occur, which disables to compute time_delta.
        Not to overcomplicate dropping these records during the scraping, we just look up to the first non-featured review
        through while and try&except loop.
        """
        if self.min_date != self.no_min_date:
            if len(self.data) > 0:
                last_date = None
                t = 1
                while last_date == None:
                    try:
                        last_date = datetime.datetime.strptime(
                                '-'.join(
                                    [str(self.data[-t]['Year']), str(self.data[-t]['Month']), str(self.data[-t]['Day'])]
                                    ), '%Y-%m-%d'
                            )
                    except:
                        t += 1
                return last_date > self.min_date
            else:
                return True
        else:
            return False # as it is not applied

    
    def _parseMainText(self):
        """
        Parse review main text. This usually contains information about the relationship of the reviewer and company.
        """
        try:
            self.mainText = re.search('<p class="mainText mb-0">(.+?)</p>', self.reviewHTML).group(1)
        except:
            self.mainText = str()
    
    def _parseRecommendationBar(self):
        """
        A function that handles parsing the whole recommendation bar into a single elements
            - recommendation of a company - (with values of recommends, doesn't recommend, none)
            - outlook; values - (with values of positive, neutral, negative, none)
            - approves of ceo - (with values of approves, no opinon, disapproves, none)
        """
        try:
            self.recommendationBar = {}
            recommendationBar = re.findall('<div class="col-sm-4">(.+?)</div>', self.reviewHTML)
            self.recommendationBarItems = [re.search('<span>(.+?)</span>', item).group(1) for item in recommendationBar]
            
            self.recommendationBar['Recommendation'] = self._parseRecommendationBar_Recommendation()
            self.recommendationBar['Outlook'] = self._parseRecommendationBar_Outlook()
            self.recommendationBar['OpinionOfCEO'] = self._parseRecommendationBar_CEO()
            
        except: # it is applied when no element of recommendation bar is present in a given review
            self.recommendationBar = {
                'Recommend': None,
                'Outlook': None,
                'CEO': None
            }
    
    def _parseRecommendationBar_CEO(self):
        """
        A helper function returning a reviewer's opinion of CEO.
        """
        try:
            itemCEO = [' '.join(item.split()[:-2]) for item in self.recommendationBarItems if 'ceo' in item.lower()]
            return itemCEO[0]
        except:
            return ''
    
    def _parseRecommendationBar_Outlook(self):
        """
        A helper function returning a reviewer's outlook on a company.
        """
        try:
            itemOutlook = [item.split()[0] for item in self.recommendationBarItems if 'outlook' in item.lower()]
            return itemOutlook[0]
        except:
            return ''

    def _parseRecommendationBar_Recommendation(self):
        """
        A helper function returning a statement whether a reviewer would recommend a given company.
        """
        try:
            itemRecommendation = [item for item in self.recommendationBarItems if 'recommend' in item.lower()]
            return itemRecommendation[0]
        except:
            return ''
    
    def _parseReviewBody(self):
        """
        Parse review body containing 'Pros', 'Cons' and 'Advice to management element'   
        """
        _reviewHTML = re.sub('\r|\n', '', self.reviewHTML)
        tabs = re.findall(  '<p class="strong mb-0 mt-xsm">(.+?)</p>', _reviewHTML)
        tabsText=re.findall(
            '<p class="mt-0 mb-xsm v2__EIReviewDetailsV2__bodyColor v2__EIReviewDetailsV2__lineHeightLarge v2__EIReviewDetailsV2__isExpanded ">(.+?)</p>',
            _reviewHTML
        )
        self.parsedReviewBody = {tab: tabText for tab, tabText in zip(tabs, tabsText)}

    def _parseReviewElements(self):
        """
        There are multiple objects in a review which need to be parsed.
        This function unites all the individual components together.
        Usage of this function is appropraite as it enables someone to avoid
        using one sub-fuction more than once (as this would be redundant).
        """
        self._parseRecommendationBar() # necessary to obtain attributes: 'Recommendation', 'Outlook', 'OpinionOfCEO'
        self._parseReviewBody() # necessary to obtain attributes: 'Pros', 'Cons' and 'Advice to Management'
        self._parseMainText() # this contains information on whether an employee is/was full-time/part-time and on a period of contract
        self._parseTimestamp() # get a timestamp

    def _parseTimestamp(self):
        """
        Parse review timestamp from review-HTML if available.
        """
        try:
            self.timestamp = re.search('<time class="date subtle small" datetime="(.+?)">', self.reviewHTML).group(1)
        except:
            self.timestamp = 'Featured Review'
    
    def _selectFirstCompany(self):
        """
        If more companies are found under a given keyword, the first returned result is chosen by this function.
        """
        try:
            if len(self.driver.find_elements_by_class_name('single-company-result')) > 0:
                firstCompany = self.driver.find_elements_by_class_name('single-company-result')[0]
            else:
                firstCompany = self.driver.find_elements_by_class_name('single-company-result module ')[0]
            
            companyLink = re.search(
               f'<a href="(.+?)">(.+?)</a>',
                firstCompany.get_attribute('outerHTML')).group(1).split()[0].strip('"')
            link = 'https://www.glassdoor.com' + companyLink
            print(link)
            self.getURL(link)
            time.sleep(1)
        except:
            self.page = float(np.inf)

    def _signIn(self):
        """
        The function that logs a driver in to a Glassdoor account.
        """
        login_url='https://www.glassdoor.com/profile/login_input.htm'
        self.getURL(login_url)
        
        if self._isLoginRequired():
            try:
                self.driver.find_element_by_name('username').send_keys(self.email)
                self.driver.find_element_by_name('password').send_keys(self.password)
                self.driver.find_element_by_xpath('//button[@type="submit"]').click()
                print('Login was successful.')
            except:
                print('Login was NOT successful.')
        else:
            pass
    
    def _signInWhite(self):
        """
        The function that logs a driver in to a Glassdoor account.
        """
        self.driver.find_element_by_xpath('/html/body/div[4]/div/div/div/div/div/div/div/div[2]/div/a').click()
        self.driver.find_element_by_name('username').send_keys(self.email)
        self.driver.find_element_by_name('password').send_keys(self.password)
        element = self.driver.find_element_by_xpath('//button[@type="submit"]')
        self.driver.execute_script("arguments[0].click();", element)
        print('Login was successful.')
    
    def _sortReviewsMostRecent(self):
        """
        This function sorts the reviews so that most recent ones are liste first.
        As it is complicated to unroll list with sorting optins, url address is amended with an appendix
        """
        url = self.driver.current_url + '?sort.sortType=RD&sort.ascending=false'
        self.getURL(url)
    
    def _checkIfDjangoRowExist(self, datarow):
        """
        """
        try:
            self.ReviewWriter.objects.get(
                Company = datarow['Company'],
                ReviewTitle = datarow['ReviewTitle'],
                Year = datarow['Year'],
                Month = datarow['Month'],
                Day = datarow['Day'],
                Rating = datarow['Rating'],
                JobTitle = datarow['JobTitle'],
                EmployeeRelationship = datarow['EmployeeRelationship'],
                Location = datarow['Location'],
                Recommendation = datarow['Recommendation'],
                Outlook = datarow['Outlook'],
                OpinionOfCEO = datarow['OpinionOfCEO'],
                Contract = datarow['Contract'],
                ContractPeriod = datarow['ContractPeriod'],
                Pros = datarow['Pros'],
                Cons = datarow['Cons'],
                AdviceToManagement = datarow['AdviceToManagement']
            )
            return True
        except self.ReviewWriter.DoesNotExist:
            return False
    
    def _writeRowToDjangoDB(self, datarow):
        """
        This function takes care of writin the single review record into a Django database.
        :param datarow: A single record (review); type=dict
        """
        try:    
            if not self._checkIfDjangoRowExist(datarow):
                reviewRecord = self.ReviewWriter(
                    Company = datarow['Company'],
                    ReviewTitle = datarow['ReviewTitle'],
                    Year = datarow['Year'],
                    Month = datarow['Month'],
                    Day = datarow['Day'],
                    Rating = datarow['Rating'],
                    JobTitle = datarow['JobTitle'],
                    EmployeeRelationship = datarow['EmployeeRelationship'],
                    Location = datarow['Location'],
                    Recommendation = datarow['Recommendation'],
                    Outlook = datarow['Outlook'],
                    OpinionOfCEO = datarow['OpinionOfCEO'],
                    Contract = datarow['Contract'],
                    ContractPeriod = datarow['ContractPeriod'],
                    Pros = datarow['Pros'],
                    Cons = datarow['Cons'],
                    AdviceToManagement = datarow['AdviceToManagement'],
                    Timestamp = datarow['Timestamp']
                )
                reviewRecord.save()
            else:
                pass
        except Exception as e:
            print(e)