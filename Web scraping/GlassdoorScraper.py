# set hyperparameters
path_chrome_driver = "/mnt/c/Data/UCL/@MSC Project/Web scraping/chromedriver.exe"
url = "https://www.glassdoor.com/Reviews/index.htm"


# set some user parameters
email = "daniel.stancl@gmail.com"
company_name = "Intel Corporation"
location = "London"
sleep_time = 0.5

# import libraries
import time
import re
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class GlassdoorScraper(object):
    """
    """
    #####################
    ### MAGIC METHODS ###
    #####################

    def __init__(self, path_chrome_driver, url, email):
        """
        Instantiate method.
        :param path_chrome_drive:
        :param url:
        :param email:
        """
        options = webdriver.ChromeOptions()
        # initialize the driver
        self.driver = webdriver.Chrome(
            executable_path=path_chrome_driver,
            options=options
        )
        # set the driver's convenient    position to look at
        self.driver.set_window_size(960, 1080)
        self.driver.set_window_position(0,0)
        # store url, email
        self.url = url
        self.email = email

    ######################
    ### PUBLIC METHODS ###
    ## major func first ##
    # alphabetical order #
    ######################

    def scrape(self, company_name, location, limit = float(np.inf)):
        """
        MAIN FUNCTION (tba)
        :param company_name:
        :param location:
        :param limit:
        """
        self.getOnReviewsPage(company_name, location)
        while page <= limit:
            page+=1

    def getOnReviewsPage(self, company_name, location):
        """
        Function that get users at on the first page of reviews for a given company.
        :param company_name:
        :param location:
        """
        self.getURL()
        self.searchReviews(company_name, location)
        self._clickReviewsButton()
        time.sleep(1)
        if self._loginRequired():
            self._loginGoogle()

        
    def getURL(self):
        """
        Get on the Glassdoor review main page.
        """
        self.driver.get(self.url)
        time.sleep(1)
    
    def getReviews(self):
        """
        A function returning a list of WebElements corresponding to individual 
        reviews displayed on a given page.
        There are two classes of empReview hence must be collected in two steps.
        """
        self.reviews = self.driver.find_elements_by_xpath('//li[@class="empReview cf"]')
        self.reviews.extend(self.driver.find_elements_by_xpath('//li[@class="noBorder empReview cf"]'))    

    def searchReviews(self, company_name, location):
        """
        :param company_name:
        :param location:
        """
        self._fillCompanyName(company_name)
        self._fillLocation(location)
        self._clickSearchButton()
        self.page = 1
        time.sleep(1)
    
    def parseReview(self):
        """
        :param reviewHTML:
        """
        return pd.Series(
            {
                'ReviewTitle': self._getReviewTitle(),
                'Timestamp': self._getTimestamp(),
                'Rating': self._getRating(),
                'JobTitle': self._getJobTitle(),
                'Location': self._getLocation(),
                'RecomendationBar': self._getRecommendationBar(),
                'MainText': self._getMainText(),
                'Pros': self._getReviewBody(element='Pros'),
                'Cons': self._getReviewBody(element='Cons'),
                'Advice to Management': self._getReviewBody(element='Advice to Management'),
            }
        )

    def acceptCookies(self):
        """
        Accept cookies consent if displayed.
        """
        try:
            self.driver.find_elements_by_id('onetrust-accept-btn-handler').click()
        except:
            print('No cookies consent is required to accept.')
    
    #######################
    ### PRIVATE METHODS ###
    ## alphabetical order #
    #######################

    def _clickContinueReading(self):
        """
        Click "Continue reading" button to unroll the whole version of reviews.
        """
        continue_reading_list = self.driver.find_elements_by_xpath(
            '//div[@class="v2__EIReviewDetailsV2__continueReading v2__EIReviewDetailsV2__clickable"]'
        )
        for continue_reading in continue_reading_list:
            continue_reading.click()
            time.sleep(5)
    
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

    def _fillCompanyName(self, company_name):
        """
        Fill a company name in a search field on the title page.
        :param company_name: type=str
        """
        assert type(company_name) == str, 'Param company_name must be a type of str.'
        self.driver.find_element_by_class_name("keyword").clear()
        self.driver.find_element_by_class_name("keyword").send_keys(company_name)

    def _fillEmailAndClick(self, email):
        """
        Fill a user e-mail to log in a Glassdoor account.
        :param email: type=str
        """
        assert type(email) == str, 'Param email must be a type of str.'
        self.driver.find_element_by_xpath('//*[@id="identifierId"]').clear()
        self.driver.find_element_by_xpath('//*[@id="identifierId"]').send_keys(email)
        self.driver.find_element_by_xpath('//*[@id="identifierNext"]/span/span').click()

    def _fillLocation(self, location):
        """
        Fill a company name in a search field on the title page.
        :param location: type=str
        """
        assert type(location) == str, 'Param locaation must be a type of str.'
        self.driver.find_element_by_class_name("loc").clear()
        self.driver.find_element_by_class_name("loc").send_keys(location)

    def _fillPasswordAndClick(self):
        """
        Fill a user password to log in a Glassdoor account. Password is asked to be typed.
        """
        self.driver.find_element_by_xpath('//*[@id="password"]/div[1]/div/div[1]/input').clear()
        self.driver.find_element_by_xpath('//*[@id="password"]/div[1]/div/div[1]/input').send_keys(input())
        self.driver.find_element_by_xpath('//*[@id="passwordNext"]/span/span').click()

    def _getJobTitle(self):
        """
        Parse reviewer's job title from review-HTML if available.
        :param reviewHTML: HTML code of a review page returned by a function _getReviewHTML, type=str
        """
        try:
            return re.search('<span class="authorJobTitle middle reviewer">(.+?)</span>', self.reviewHTML).group(1)
        except:
            return None
    
    def _getLocation(self):
        """
        Parse reviewr's job location from review-HTML if available.
        """
        try:
            return re.search('<span class="authorLocation">(.+?)</span>', self.reviewHTML).group(1)
        except:
            return None

    def _getMainText(self):
        """
        Parse review main text. This usually contains information about the relationship of the reviewer and company.
        """
        try:
            return re.search('<p class="mainText mb-0">(.+?)</p>', self.reviewHTML).group(1)
        except:
            return None
    
    def _getRating(self):
        """
        Parse review rating from review-HTML if available.
        """
        try:
            return re.search('<div class="v2__EIReviewsRatingsStylesV2__ratingNum v2__EIReviewsRatingsStylesV2__small">(.+?)</div>', self.reviewHTML).group(1)
        except:
            return None

    def _getRecommendationBar(self):
        """
        Parse recomendation bar containing items/attributes like ('positive outlook', 'approves of CEO') etc.
        All the items are concatenated to a string by ' | '.
        """
        try:
            recomendationBarItems = re.findall('<div class="col-sm-4">(.+?)</div>', self.reviewHTML)
            return ' | '.join(re.search('<span>(.+?)</span>', item).group(1) for item in recomendationBarItems)
        except:
            return None
    
    def _getReviewBody(self, element):
        """
        Get individual elements of the review body
        :param element: A string indicating a component of a review body
            select from: ['Pros', 'Cons', 'Advice to Management'], type=str
        """
        assert type(element) == str, 'Param element must be a type of str.'
        assert element in ['Pros', 'Cons', 'Advice to Management'], "Element must be drawn from the list ['Pros', 'Cons', 'Advice to Management']."
        try:
            return self.parsedReviewBody[element]
        except:
            return None
    
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
            return None
    
    def _getTimestamp(self):
        """
        Parse review timestamp from review-HTML if available.
        """
        try:
            return re.search('<time class="date subtle small" datetime="(.+?)">', self.reviewHTML).group(1)
        except:
            return None

    def _isNextPageAvailable(self):
        """
        Needs to be finished.
        The ultimate functionality is to find out whether the next page
        contains any review. If not, scraping should be terminated. 
        """
        if '_P' in self.driver.current_url:
            next_url = re.sub('_P(.+?).htm', f'_P{(self.page)+1}.htm', self.driver.current_url)
        else:
            next_url = re.sub('.htm', '_P2.htm', self.driver.current_url)
    
    def _loginGoogle(self):
        """
        A module capable to log in to user's Google account connected with to a Glassdoor account.
        All the operations from clicking on the button, switching windows to filling user's details
        are handled within this single function.
        """
        self.driver.find_element_by_xpath('//*[@id="HardsellOverlay"]/div/div/div/div/div/div/div/div[1]/div[1]/div/div[2]/button').click()
        time.sleep(0.5)
        self.driver.switch_to.window(self.driver.window_handles[1])
        self._fillEmailAndClick(self.email)
        time.sleep(0.5)
        try:
            print('Type your password.')
            self._fillPasswordAndClick()
        except:
            print('Mobile verification is required.')
        self.driver.switch_to.window(self.driver.window_handles[0])

    def _loginRequired(self):
        """
        A function that is responsible for detecting whether a user is required to log in its Glassdoor account.
        """
        return len(self.driver.find_elements_by_xpath('//*[@id="HardsellOverlay"]/div/div/div/div/div/div/div/div[1]/div[1]/div/div[2]/button')) > 0
    
    def _parseReviewBody(self, reviewHTML):
        """
        Parse review body containing 'Pros', 'Cons' and 'Advice to management element'   
        :param reviewHTML:
        """
        _reviewHTML = re.sub('\r|\n', '', reviewHTML)
        tabs = re.findall('<p class="strong mb-0 mt-xsm">(.+?)</p>', _reviewHTML)
        tabsText=re.findall(
            '<p class="mt-0 mb-xsm v2__EIReviewDetailsV2__bodyColor v2__EIReviewDetailsV2__lineHeightLarge v2__EIReviewDetailsV2__isExpanded ">(.+?)</p>',
            _reviewHTML
        )
        self.parsedReviewBody = {tab: tabText for tab, tabText in zip(tabs, tabsText)}
       

    


# application (still needs to be automated in scrape module)
scraper = GlassdoorScraper(path_chrome_driver, url, email)
scraper.getURL()
scraper.searchReviews(
    company_name='Intel Corporation',
    location='London'
)
time.sleep(1.0)
scraper._clickReviewsButton()
scraper.loginGoogle()
scraper._clickContinueReading()
scraper.driver.find_element_by_id('onetrust-accept-btn-handler').click()
scraper._clickContinueReading()
scraper.getReviews()





reviews = scraper.reviews
reviews.extend(scraper.driver.find_elements_by_xpath('//li[@class="noBorder empReview cf"]'))

j=0
review = reviews[j]
reviewHTML = review.get_attribute('outerHTML')
reviewHTML = re.sub('\r|\n', '', reviewHTML)
tab=re.findall('<p class="strong mb-0 mt-xsm">(.+?)</p>', reviewHTML)
tab
tabText=re.findall(
    '<p class="mt-0 mb-xsm v2__EIReviewDetailsV2__bodyColor v2__EIReviewDetailsV2__lineHeightLarge v2__EIReviewDetailsV2__isExpanded ">(.+?)</p>',
    reviewHTML
)
tabText





reviewText = scraper.driver.find_elements_by_xpath('//li[@class="noBorder empReview cf"]')[0].get_attribute('outerHTML')
reviewText

reviewText = scraper.reviews[2].get_attribute('innerHTML')
tab=re.findall('<p class="strong mb-0 mt-xsm">(.+?)</p>', reviewText)
tab
tabText=re.findall(
    '<p class="mt-0 mb-xsm v2__EIReviewDetailsV2__bodyColor v2__EIReviewDetailsV2__lineHeightLarge v2__EIReviewDetailsV2__isExpanded ">(.+?)</p>',
    reviewText
)
tabText
print(len(tabText))


len(scraper.reviews)