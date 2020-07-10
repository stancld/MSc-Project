from GlassdoorScraper import *

# parameters
chrome_driver_path = '/mnt/c/Data/UCL/@MSC Project - Data and sources/chromedriver.exe'

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