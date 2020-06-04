# set some user parameters
email = "daniel.stancl@gmail.com"

# import libraries
from selenium import webdriver
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
driver.find_element_by_class_name("loc").send_keys("London")

# 3. Click on the search button
driver.find_element_by_class_name("gd-btn-mkt").click()

# 4. Click on reviews button (reviews tab)
driver.find_element_by_xpath('//*[@id="EIProductHeaders"]/div/a[1]').click()

# 5. Sign for a free use (if it is asked)
try:
    # click on login via Google
    driver.find_element_by_xpath('//*[@id="HardsellOverlay"]/div/div/div/div/div/div/div/div[1]/div[1]/div/div[2]/button').click()
    # switch to the new window
    driver.switch_to.window(driver.window_handles[1])
    # fill in an e-mail address and click on next
    driver.find_element_by_xpath('//*[@id="identifierId"]').clear()
    driver.find_element_by_xpath('//*[@id="identifierId"]').send_keys(email)
    driver.find_element_by_xpath('//*[@id="identifierNext"]/span/span').click()
    # fill in a password and click on next
    driver.find_element_by_xpath('//*[@id="password"]/div[1]/div/div[1]/input').clear()
    driver.find_element_by_xpath('//*[@id="password"]/div[1]/div/div[1]/input').send_keys(input())
    driver.find_element_by_xpath('//*[@id="passwordNext"]/span/span').click()
    # switch to the original window
    driver.switch_to.window(driver.window_handles[0])
except:
    pass

# get reviews
reviews = driver.find_elements_by_class_name("review")
reviews


