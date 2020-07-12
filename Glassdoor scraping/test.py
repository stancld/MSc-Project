from GlassdoorScraper import *

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# parameters
chrome_driver_path = '/mnt/c/Data/UCL/@MSC Project - Data and sources/chromedriver.exe'


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-certificate-errors-spki-list')
chrome_options.add_argument('--ignore-ssl-errors')

driver = webdriver.Chrome(
    executable_path=chrome_driver_path,
    options=chrome_options
)
driver.set_window_size(1440, 1080)


driver.find_element_by_xpath('/html/body/div[4]/div/div/div/div/div/div/div/div[2]/div/a').click()

driver.find_element_by_name('username').send_keys('q12')
driver.find_element_by_name('password').send_keys('q12')
driver.find_element_by_xpath('//button[@type="submit"]')



credentials = '/mnt/c/Data/UCL/@MSc Project - Data and sources/credentials.json'
with open(args.credentials) as f:
    credentials = json.loads(f.read())
    args.email = credentials['email']
    args.password = credentials['password']

headless_browsing = False

mysite_path = '/mnt/c/Data/UCL/@MSc Project/DB/mysite/'
set_django_db(mysite_path=args.mysite_path)
from tables_daniel.models import Review, Company
review_writer = Review
company_reader = Company

max_review_age = None