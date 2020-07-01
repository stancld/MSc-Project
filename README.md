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

## Description of the functionality of scraper tools

## Installation of scraper tools
1. Check, you're python of version >3.7
2. Clone/downloadn this repository
3. Install all necessary dependencies via running `pip install -r requirements.txt` inside this repo.
4. Install [ChromeDriver](http://chromedriver.chromium.org/). The path to the driver is then specified when you run the script itself.
5. When you want to log in [Glassdoor](https://www.glassdoor.com/member/home/index.htm) an email and password are required to access your account. Hence, first create an account at [Glassdoor](https://www.glassdoor.com/member/home/index.htm) and, subsequently, create a file `credentials.json` containing `email` and `password` elements.

## Usage of scraper tools
#### 1. Wikipedia & Yahoo Scraper
```
usage: main.py [-h] [--stock_indices STOCK_INDICES] [--use_django_db USE_DJANGO_DB]
               [--mysite_path MYSITE_PATH] [--output_path OUTPUT_PATH]

optional arguments:
  -h --help                         Show this help message and exit.
  --stock_indices STOCK_INDICES     A list of stock indices that should be scraped.
                                    Currently supported: ['S&P 500, 'FTSE 100', 'EURO STOXX 50']
  --use_django_db USE_DJANGO_DB     A boolean indiciation whether the data should be stored in django DB.
  --mysite_path MYSITE_PATH         An absolute path to the django application containing models for the DB.
                                    This is required iff use_django_db is passed in.
  --output_path OUTPUT_PATH         An absolute path of the output csv/xlsx file storing the scraped data.
                                    This is required iff use_django_db is not passed in.
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
```
