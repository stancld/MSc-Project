# Employee Sentiment Analysis for ESG Investing (MSc Project)

- Author: Daniel Stancl
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
3. Install all necessary dependencies via running `pip install -r requirements.txt` or `pip3 install -r requirements.txt` inside this repo.
4. Install [ChromeDriver](http://chromedriver.chromium.org/). The path to the driver is then specified when you run the script itself.
5. When you want to log in [Glassdoor](https://www.glassdoor.com/member/home/index.htm) an email and password are required to access your account. Hence, first create an account at [Glassdoor](https://www.glassdoor.com/member/home/index.htm) and, subsequently, create a file `credentials.json` containing `email` and `password` elements.

## Usage of scraper tools
**1. Wikipedia & Yahoo Scraper**
```
usage: main.py [-h] [--stock_indices STOCK_INDICES] [--

optional arguments:
```
