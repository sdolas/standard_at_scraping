import datetime 
import pandas as pd
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from selenium import webdriver as wd



##### GET ALL URLS
scraped_urls = list()

# OPEN CHROME
driver = wd.Chrome(r'C:\Users\user00\Documents\selenium webdriver chrome\chromedriver.exe')

# GET PAGE
baseurl = "https://www.derstandard.at/frontpage/"
datum = datetime.datetime(1999,1,11)

# erste Seite laden
url = baseurl + datum.strftime("%Y/%m/%d")
driver.get(url)
time.sleep(1)

# werbung akzeptieren
driver.switch_to.frame(driver.find_element(By.XPATH, "/html/body/div/iframe"))
driver.find_element(By.XPATH, "/html/body/div/div[2]/div[3]/div[1]/button").click()
time.sleep(15)

# pushs ablehnen
driver.find_element(By.XPATH, "/html/body/div[6]/div[3]/div[3]/div[1]/button[1]").click()

while datum <= datetime.datetime.today():
    datum += datetime.timedelta(days=1)
    url = baseurl + datum.strftime("%Y/%m/%d")
    driver.get(url)
    soup = BeautifulSoup(driver.page_source,"html5lib")
    
    for article in soup.findAll("article"):
        scraped_urls.append(article.find("a").get("href"))

urls_df = pd.DataFrame({"url":scraped_urls})
urls_df.to_csv(r"C:\Users\user00\Documents\GitHub\standard_at_scraping\urls.csv")
urls_df.to_feather(r"C:\Users\user00\Documents\GitHub\standard_at_scraping\urls.feather")

driver.close()
