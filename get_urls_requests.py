import datetime
import pandas as pd
from bs4 import BeautifulSoup
import time
import requests
import random

##### GET ALL URLS
scraped_urls = list()

# GET PAGE
baseurl = "https://www.derstandard.at/frontpage/"
datum = datetime.datetime(2023, 4, 1)

# Liste von User-Agent-Strings
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134'
]

while datum <= datetime.datetime.today():
    datum += datetime.timedelta(days=1)
    url = baseurl + datum.strftime("%Y/%m/%d")

    headers = {'User-Agent': random.choice(user_agents)}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html5lib")

    for article in soup.findAll("article"):
        scraped_urls.append(article.find("a").get("href"))

urls_df = pd.DataFrame({"url": scraped_urls})
urls_df.to_csv(r"C:\Users\user00\Documents\GitHub\standard_at_scraping\urls.csv")
urls_df.to_feather(r"C:\Users\user00\Documents\GitHub\standard_at_scraping\urls.feather")