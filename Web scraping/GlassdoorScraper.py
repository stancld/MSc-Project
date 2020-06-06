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
    def __init__(self, path_chrome_driver, url, email):
        """
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

    def scrape(self, company_name, location, limit = float(np.inf)):
        """
        MAIN FUNCTION (tba)
        """
        self.getURL()
        time.sleep(1)
        self.searchReviews(company_name, location)
        time.sleep(1)
        self.clickReviewsButton()
        time.sleep(1)
        if self.loginRequired():
            self.loginGoogle()

        
    def getURL(self):
        """
        Get on the Glassdoor review main page.
        """
        self.driver.get(self.url)

    def searchReviews(self, company_name, location):
        """
        :param company_name:
        :param location:
        """
        self._fillCompanyName(company_name)
        self._fillLocation(location)
        self._clickSearchButton()
        self.page = 1

    def getReviews(self):
        """
        A function returning a list of WebElements corresponding to individual 
        reviews displayed on a given page.
        There are two classes of empReview hence must be collected in two steps.
        """
        self.reviews = self.driver.find_elements_by_xpath('//li[@class="empReview cf"]')
        self.reviews.extend(self.driver.find_elements_by_xpath('//li[@class="noBorder empReview cf"]'))    
    
    def parseReview(self, reviewHTML):
        """
        :param reviewHTML:
        """
        return pd.Series(
            {
                'ReviewTitle': self._getReviewTitle(reviewHTML),
                'Timestamp': self._getTimestamp(reviewHTML),
                'Rating': self._getRating(reviewHTML),
                'JobTitle': self._getJobTitle(reviewHTML),
                'Location': self._getLocation(reviewHTML),
                'RecomendationBar': self._getRecommendationBar(reviewHTML)
            }
        )
    def _getReviewHTML(self, review):
        """
        :param review:
        """
        return review.get_attribute('outerHTML')

    def _getReviewTitle(self, reviewHTML):
        """
        Parse review title from review-HTML if filled.
        """
        try:
            return re.search('reviewLink">"(.+?)"</a>', reviewHTML).group(1)
        except:
            return None
    
    def _getTimestamp(self, reviewHTML):
        """
        Parse review timestamp from review-HTML if available.
        """
        try:
            return re.search('<time class="date subtle small" datetime="(.+?)">', reviewHTML).group(1)
        except:
            return None

    def _getRating(self, reviewHTML):
        """
        Parse review rating from review-HTML if available.
        """
        try:
            return re.search('<div class="v2__EIReviewsRatingsStylesV2__ratingNum v2__EIReviewsRatingsStylesV2__small">(.+?)</div>', reviewHTML).group(1)
        except:
            return None
    
    def _getJobTitle(self, reviewHTML):
        """
        Parse reviewer's job title from review-HTML if available.
        """
        try:
            return re.search('<span class="authorJobTitle middle reviewer">(.+?)</span>', reviewHTML).group(1)
        except:
            return None

    def _getLocation(self, reviewHTML):
        """
        Parse reviewr's job location from review-HTML if available.
        """
        try:
            return re.search('<span class="authorLocation">(.+?)</span>', reviewHTML).group(1)
        except:
            return None

    def _getRecommendationBar(self, reviewHTML):
        """
        """
        try:
            recomendationBarItems = re.findall('<div class="col-sm-4">(.+?)</div>', reviewHTML)
            return ' | '.join(re.search('<span>(.+?)</span>', item).group(1) for item in recomendationBarItems)
        except:
            return None
    

    def loginGoogle(self):
        """
        :param email:
        """
        self.driver.find_element_by_xpath('//*[@id="HardsellOverlay"]/div/div/div/div/div/div/div/div[1]/div[1]/div/div[2]/button').click()
        time.sleep(0.5)
        self.driver.switch_to.window(self.driver.window_handles[1])
        self._fillEmail(self.email)
        time.sleep(0.5)
        try:
            print('Type your password.')
            self._fillPassword()
        except:
            pass
        self.driver.switch_to.window(self.driver.window_handles[0])
    
    def _fillCompanyName(self, company_name):
        """
        :param company_name:
        """
        self.driver.find_element_by_class_name("keyword").clear()
        self.driver.find_element_by_class_name("keyword").send_keys(company_name)

    def _fillLocation(self, location):
        """
        :param location:
        """
        self.driver.find_element_by_class_name("loc").clear()
        self.driver.find_element_by_class_name("loc").send_keys(location)
    
    def _clickSearchButton(self):
        """
        """
        self.driver.find_element_by_class_name("gd-btn-mkt").click()

    def clickReviewsButton(self):
        """
        """
        self.driver.find_element_by_xpath('//*[@id="EIProductHeaders"]/div/a[1]').click()

    def _clickContinueReading(self):
        """
        """
        continue_reading_list = self.driver.find_elements_by_xpath(
            '//div[@class="v2__EIReviewDetailsV2__continueReading v2__EIReviewDetailsV2__clickable"]'
        )
        for continue_reading in continue_reading_list:
            continue_reading.click()
            time.sleep(5)

    def loginRequired(self):
        """
        """
        return len(self.driver.find_elements_by_xpath('//*[@id="HardsellOverlay"]/div/div/div/div/div/div/div/div[1]/div[1]/div/div[2]/button')) > 0
    
    def _fillEmail(self, email):
        """
        :param email:
        """
        self.driver.find_element_by_xpath('//*[@id="identifierId"]').clear()
        self.driver.find_element_by_xpath('//*[@id="identifierId"]').send_keys(email)
        self.driver.find_element_by_xpath('//*[@id="identifierNext"]/span/span').click()
    
    def _fillPassword(self):
        """
        """
        self.driver.find_element_by_xpath('//*[@id="password"]/div[1]/div/div[1]/input').clear()
        self.driver.find_element_by_xpath('//*[@id="password"]/div[1]/div/div[1]/input').send_keys(input())
        self.driver.find_element_by_xpath('//*[@id="passwordNext"]/span/span').click()

    def _nextPageAvailable(self):
        """
        Needs to be finished.
        The ultimate functionality is to find out whether the next page
        contains any review. If not, scraping should be terminated. 
        """
        if '_P' in self.driver.current_url:
            next_url = re.sub('_P(.+?).htm', f'_P{(self.page)+1}.htm', self.driver.current_url)
        else:
            next_url = re.sub('.htm', '_P2.htm', self.driver.current_url)
    
    def acceptCookies(self):
        self.driver.find_elements_by_id('onetrust-accept-btn-handler').click()

    


# application (still needs to be automated)
scraper = GlassdoorScraper(path_chrome_driver, url, email)
scraper.getURL()
scraper.searchReviews(
    company_name='Intel Corporation',
    location='London'
)
time.sleep(1.0)
scraper.clickReviewsButton()
scraper.loginGoogle()
scraper._clickContinueReading()
scraper.driver.find_element_by_id('onetrust-accept-btn-handler').click()
scraper._clickContinueReading()
scraper.getReviews()

for 

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