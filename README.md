# Employee Sentiment Analysis for ESG Investing (MSc Project)

- **Author: Daniel Stancl**
- University: UCL
- Program: MSc Computational Statistics and Machine Learning
- Supervisor: Prof Philip Treleaven
- Industry Partner: Fidelity International
- Academic year: 2019/2020

<hr>

## Description of MSc Project
The aim of this industry-based project, conducted in a cooperation with Fidelity International, is to create a regularly refreshed database (implemented in Django) containing employee reviews listed on Glassdoor.com (scraped with Selenium). Subsequently, the sentiment of the reviews are to be scored with pre-trained language models and the results are to be incorporated into the multi-factor credit scoring model as a part of ESG investing framework.

## Disclaimer
Scraping the content from Wikipedia and Yahoo webpages is forbidden by their Terms of Service. While it is unlikely to be banned from this websites, please, use the scraper wisely, and even better with an express written permission of representatives of given webpages.

Scraping the content from Glassdoor webpages is forbidden by their Terms of Use, section 3B (Using Glassdoor - House Rules). As such, please do not use this scraper without their express written permission. Furthermore, I do not claim responsibility for banning your Glassdoor account should the scraper be used too heavily. Moreover, should I be connacted by a representative of Glassdoor to remove this repo/make this repo private, I will do so.

Please if any, use all the tools wisely.

## Description of the functionality of scraper tools

## Installation of scraper tools
1. Check, you're using python of version >3.7
2. Clone/downloadn this repository
3. Install all necessary dependencies via running `pip install -r requirements.txt` inside this repo.
4. Install [ChromeDriver](http://chromedriver.chromium.org/). The path to the driver is then specified when you run the script itself.
5. When you want to log in [Glassdoor](https://www.glassdoor.com/member/home/index.htm) an email and password are required to access your account. Hence, first create an account at [Glassdoor](https://www.glassdoor.com/member/home/index.htm) and, subsequently, create a file `credentials.json` containing `email` and `password` elements.

## Usage of scraper tools
#### 1. Wikipedia & Yahoo Scraper
```
usage: main.py [-h] [--stock_indices STOCK_INDICES]
               [--mysite_path MYSITE_PATH] [--output_path OUTPUT_PATH]

optional arguments:
  -h --help                         Show this help message and exit.
  --stock_indices STOCK_INDICES     A list of stock indices that should be scraped.
                                    Currently supported: ['S&P 500, 'FTSE 100', 'EURO STOXX 50']
  --mysite_path MYSITE_PATH         An absolute path to the django application containing models for the DB.
                                    This is required iff output_path is not passed in.
  --output_path OUTPUT_PATH         An absolute path of the output csv/xlsx file storing the scraped data.
                                    This is required iff mysite_path is not passed in.
```
**Examples**
1. *Running the script with django db.*
```
python main.py --stock_indices ['S&P 500', 'FTSE 100', 'EURO STOXX 50'] --use_django_db --mysite_path '/mnt/c/mysite/'
```
This command downloads all the firms which are listed on *S&P 500, FTSE 100, EURO STOXX 50* stock indices and store them in a connected django database.

2. *Running the script with saving the scraped data in an xlsx file.*
```
python main.py --stock_indices ['S&P 500', 'FTSE 100', 'EURO STOXX 50'] --output_path '/mnt/c/data/companies.xlsx'
```
This command downloads all the firms which are listed on *S&P 500, FTSE 100, EURO STOXX 50* stock indices and store them in `companies.xlxs` within a defined folder.

#### 2. Glassdoor Scraper
```
usage: main.py [-h] [--chrome_driver_path CHROME_DRIVER_PATH] [--headless]
               [--email EMAIL] [-p PASSWORD] [-c CREDENTIALS]
               [--max_review_age MAX_REVIEW_AGE] [-u URL] [--location LOCATION]
               [--mysite_path MYSITE_PATH] [--output_path OUTPUT_PATH] [-l LIMIT]
               
optional argument:
  -h --help                                     Show this help message and exit.
  --chrome_driver_path CHROME_DRIVER_PATH        An absolute path to the ChromeDriver.
  --headless                                    If --headless is passed in, the `headless` browsing is used.
  -e EMAIL --email EMAIL                        Email used for log in to the Glassdoor account
  -p PASSWORD --password PASSWORD               Password used for log in to the Glassdoor account
  -c CREDENTIALS --credentials CREDENTIALS      Path to credential file containing email and password
                                                used for log in to the Glassdoor account.
  --max_review_age MAX_REVIEW_AGE               An indication how old reviews are to be scraped.
                                                Default=2
  --location LOCATION                           A location we are interested in.
                                                Default='London'
  --mysite_path MYSITE_PATH                     An absolute path to the django application containing models for the DB.
                                                This is required iff output_path is not passed in.
  --output_path OUTPUT_PATH                     An absolute path of the output csv/xlsx file storing the scraped data.
                                                This is required iff mysite_path is not passed in.
  -l LIMIT --limit LIMIT                        A number of pages to be scraped.
                                                This is an ideal option for testing, otherwise no limit is passed.
```
**Examples**
1. *Running the script with a headless browser, using existing credentials and storing the scraped data within a database*
```
python main.py --chrome_driver_path '/mnt/c/data/chromedriver/ --headless -c '/mnt/c/data/credentials.json'
--max_review_age 3 --location 'New York', --mysite_path '/mnt/c/mysite'
```
This command downloads all the reviews with a maximum age of 3 years. Headless browsing is used and eventually all the scraped data are pushed into a django DB specified by mysite_path.

2. *Running the script for testing with no advanced options.*
```
python main.py --chrome_driver_path '/mnt/c/data/chromedriver/ -e <user_email> -p <user_password> --output_path '/mnt/c/data/reviews.csv' -l 10
```
