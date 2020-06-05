# set some user parameters
email = "daniel.stancl@gmail.com"
location = "London"
sleep_time = 0.5

# import libraries
import time
import re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# set some options and parameters
options = webdriver.ChromeOptions()
path_chrome_driver = "/mnt/c/Data/UCL/@MSC Project/Web scraping/chromedriver.exe"
url = "https://www.glassdoor.com/Reviews/index.htm"

# initialize the driver
driver = webdriver.Chrome(
    executable_path=path_chrome_driver,
    options=options
)
# set the driver proper position to look at
driver.set_window_size(960, 1080)
driver.set_window_position(0,0)

# get url 
driver.get(url)

#### some hacks ####
# 1. Clear text field for keyword (=company name) and fill t
driver.find_element_by_class_name("keyword").clear()
driver.find_element_by_class_name("keyword").send_keys("Intel Corporation")

# 2. Clear and define location
driver.find_element_by_class_name("loc").clear()
driver.find_element_by_class_name("loc").send_keys(location)

# 3. Click on the search button
driver.find_element_by_class_name("gd-btn-mkt").click()
time.sleep(sleep_time)

# 4. Click on reviews button (reviews tab)
driver.find_element_by_xpath('//*[@id="EIProductHeaders"]/div/a[1]').click()

# 5. Sign for a free use (if it is asked)
time.sleep(sleep_time)
# click on login via Google
driver.find_element_by_xpath('//*[@id="HardsellOverlay"]/div/div/div/div/div/div/div/div[1]/div[1]/div/div[2]/button').click()
time.sleep(sleep_time)
# switch to the new window
driver.switch_to.window(driver.window_handles[1])
# fill in an e-mail address and click on next
driver.find_element_by_xpath('//*[@id="identifierId"]').clear()
driver.find_element_by_xpath('//*[@id="identifierId"]').send_keys(email)
driver.find_element_by_xpath('//*[@id="identifierNext"]/span/span').click()
# fill in a password and click on next (if asked; sometimes telephone check is raised)
time.sleep(0.5)
driver.find_element_by_xpath('//*[@id="password"]/div[1]/div/div[1]/input').clear()
driver.find_element_by_xpath('//*[@id="password"]/div[1]/div/div[1]/input').send_keys(input())
driver.find_element_by_xpath('//*[@id="passwordNext"]/span/span').click()
# switch to the original window
driver.switch_to.window(driver.window_handles[0])
# Expand all the reviews on a given page
continue_reading_list = driver.find_elements_by_xpath('//div[@class="v2__EIReviewDetailsV2__continueReading v2__EIReviewDetailsV2__clickable"]')
for continue_reading in continue_reading_list:
    continue_reading.click()
    time.sleep(5)


# get all the reviews on a given page
reviews = driver.find_elements_by_xpath('//li[@class="empReview cf"]')
review=reviews[1]

# get outerHTML of REVIEWS element
reviewText = review.get_attribute('outerHTML')

# get review title
re.search('reviewLink">"(.+?)"</a>', reviewText).group(1)

# get timestamp
re.search('<time class="date subtle small" datetime="(.+?)">', reviewText).group(1)

# get rating 
re.search('<div class="v2__EIReviewsRatingsStylesV2__ratingNum v2__EIReviewsRatingsStylesV2__small">(.+?)</div>', reviewText).group(1)

# get job title
re.search('<span class="authorJobTitle middle reviewer">(.+?)</span>', reviewText).group(1)

# get location
re.search('<span class="authorLocation">(.+?)</span>', reviewText).group(1)

# recommendation bar
[re.search('<span>(.+?)</span>', item).group(1) for item in re.findall('<div class="col-sm-4">(.+?)</div>', reviewText)]

# get review main text
re.search('<p class="mainText mb-0">(.+?)</p>', reviewText).group(1)

# get pros, cons, advice to management
tab=re.findall('<p class="strong mb-0 mt-xsm">(.+?)</p>', reviewText)

tabText=re.findall(
    '<p class="mt-0 mb-xsm v2__EIReviewDetailsV2__bodyColor v2__EIReviewDetailsV2__lineHeightLarge v2__EIReviewDetailsV2__isExpanded ">(.+?)</p>',
    reviewText
)
{key: val for key, val in zip(tab, tabText)}






# dealing with next page
# button on the next page
driver.find_element_by_xpath('//*[@id="NodeReplace"]/main/div/div[1]/div[7]/ul/li[7]/a').click()
driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + "t")
URL=driver.current_url
URL='https://www.glassdoor.com/Reviews/Intel-Corporation-Reviews-E1519_P2.htm'
driver.get(URL)