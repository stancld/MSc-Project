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
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common import By
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

    def scrape(self, company_name, location, limit = int(np.inf)):
        """
        """
        self.getURL()
        time.sleep(1)
        self.searchReviews(company_name, location)
        time.sleep(1)
        self.clickReviewsButton()
        time.sleep(1)
        if self.loginRequired():
            self.loginGoogle(self.email)
        ####
        
        
    def getURL(self):
        """
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
        """
        self.reviews = self.driver.find_elements_by_xpath('//li[@class="empReview cf"]')    

    def loginGoogle(self, email):
        """
        :param email:
        """
        self.driver.switch_to.window(self.driver.window_handles[1])
        self._fillEmail(email)
        time.sleep(0.5)
        print('Type your password.')
        self._fillPassword()
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
        current_url = self.driver.current_url
        if '_P' in current_url:
            next_url = re.sub('_P(.+?).htm', f'_P{self.i+1}.htm', current_url)
        else:
            next_url = re.sub('.htm', '_P2.htm', current_url)
    

url = 'https://www.glassdoor.com/Reviews/Intel-Corporation-Reviews-E1519_P87.htm'
i=83
re.sub('_P(.+?).htm', f'_P{i}.htm', url)
re.sub()