# Employee Sentiment Analysis for Factor Investing in the Corporate Bond Market (MSc Project)

- **Author: Daniel Stancl**
- University: UCL
- Program: MSc Computational Statistics and Machine Learning
- Supervisor: Prof Philip Treleaven
- Industry Partner: Fidelity International
- Academic year: 2019/2020

<hr>

## Abstract
This thesis investigates the relationship between employee sentiment, proxied by [Glassdoor](https://www.glassdoor.com) reviews and ratings, and excessive returns on corresponding bonds. While sentiment analysis is well studied for probing into how companies are perceived by investors or the general public, it is a novel idea to exploit sentiment of employees, which enables us to capture very important information for assessing companies' governance. Although a few studies scrutinising the relation employee sentiment and future stock returns have already appeared, this is the first attempt, to the best of my knowledge, to place this analysis to the universe of corporate bonds.

This research was conducted in collaboration with Fidelity International and entails a series of experiments that examine how employees' feelings might be utilized as an indicator of returns on corporate bonds. This project was prepared as a separate piece of work, in cooperation with an ESG-oriented research group under the supervision of Prof. Philip Treleaven. 


The thesis consists of the following four components - a data retrieval pipeline, two experiments and an exploratory analysis:

1. Data Retrieval and Database Pipeline. This work engineers a pipeline for scraping employee reviews and related information from [Glassdoor](https://www.glassdoor.com) using a Python's Selenium-based crawler and subsequently storing them in the database built using Django making the data easily available for possible future endeavours of other students and researchers.

2. Comparison of Different Sentiment Scoring Methods in Generating Alpha. This experiment investigates the utilization of NLP sentiment analysis of employee reviews into a multi-factor credit scoring model, as a part of ESG investing framework, and their power in generating alpha by own constructed factor long-short portfolio.

3. Comparison of the Best Sentiment Scoring Method against the Usage of Reviews in Generating Alpha. This study further examines whether NLP sentiment analysis provides any additional piece of information compared with a simpler proxy for exmployee sentiment, star ratings, for generating excessive returns of factor portfolios.

4. Exploratory Analysis of Ratings and Reviews. Since analyses of reviews and ratings from [Glassdoor](https://www.glassdoor.com) and similar platforms are quite scarce, mainly because of unavailability of any public API, a thorough exploratory analysis of the scraped data is conducted as a part of this thesis and is presented at Appendix.

The following approaches are considered for sentiment scoring methods:

1. Score pros and cons separately.
    
2. Score reviews consisting of concatenated pros and cons.
    
3. Combine both approaches stated above with weighting them according to the text length.


The key findings of this thesis are:


## Disclaimer
Scraping the content from Wikipedia and Yahoo webpages is forbidden by their Terms of Service. While it is unlikely to be banned from this websites, please, use the scraper wisely, and even better with an express written permission of representatives of given webpages.

Scraping the content from Glassdoor webpages is forbidden by their Terms of Use, section 3B (Using Glassdoor - House Rules). As such, please do not use this scraper without their express written permission. Furthermore, I do not claim responsibility for banning your Glassdoor account should the scraper be used too heavily. Moreover, should I be connacted by a representative of Glassdoor to remove this repo/make this repo private, I will do so.

Please if any, use all the tools wisely.

## Description of the functionality of scraper tools

## Installation of scraper tools
1. Check, you're using python of version >3.7
2. Clone this repository via `git clone https://github.com/stancld/MSc-Project.git`
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
               [--companies COMPANIES] [--location LOCATION] [--max_review_age MAX_REVIEW_AGE]
               [--min_date MIN_DATE] [--mysite_path MYSITE_PATH] [--output_path OUTPUT_PATH]
               [-l LIMIT]
               
optional argument:
  -h --help                                     Show this help message and exit.
  --chrome_driver_path CHROME_DRIVER_PATH       An absolute path to the ChromeDriver.
  --headless                                    If --headless is passed in, the `headless` browsing is used.
  -e EMAIL --email EMAIL                        Email used for log in to the Glassdoor account
  -p PASSWORD --password PASSWORD               Password used for log in to the Glassdoor account
  -c CREDENTIALS --credentials CREDENTIALS      Path to credential file containing email and password
                                                used for log in to the Glassdoor account.
  --companies COMPANIES                         An absolute path to the list of companies (txt file).
  --location LOCATION                           A location we are interested in.
  --max_review_age MAX_REVIEW_AGE               An indication how old reviews are to be scraped.
                                                Define if min_date is not provided.
  --min_date MIN_DATE                           An indication up to which date reviews are to be scraped.
                                                Format=`yyyy-mm-dd`
                                                Define iff max_review_age is not provided.
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
--min_date '2018-06-30' --mysite_path '/mnt/c/mysite'
```
This command downloads all the reviews with a maximum age of 3 years. Headless browsing is used and eventually all the scraped data are pushed into a django DB specified by mysite_path.

2. *Running the script for testing with no advanced options.*
```
python main.py --chrome_driver_path '/mnt/c/data/chromedriver/ -e <user_email> -p <user_password> --output_path '/mnt/c/data/reviews.csv' -l 10
```
