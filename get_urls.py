import datetime 
import pandas as pd
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from selenium import webdriver as wd
import sqlite3

def get_highest_date():
    # Verbindung zur SQLite-Datenbank herstellen
    connection = sqlite3.connect(r"C:\Users\user00\Documents\GitHub\standard_at_scraping\article_data.db")
    cursor = connection.cursor()
    
    # SQL-Abfrage zum Abrufen des höchsten Datumswerts
    query = "SELECT MAX(pubdate) FROM articles"
    
    # Datumswert abrufen
    cursor.execute(query)
    result = cursor.fetchone()
    max_date = datetime.datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
    
    # Verbindung zur Datenbank schließen
    cursor.close()
    connection.close()

    # Den höchsten Datumswert in der Variablen "datum" speichern
    return max_date.date()

##### GET ALL URLS
scraped_urls = list()

# OPEN CHROME
driver = wd.Chrome(r'C:\Users\user00\Documents\selenium webdriver chrome\chromedriver.exe')

# GET PAGE
baseurl = "https://www.derstandard.at/frontpage/"
datum = get_highest_date()

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

while datum <= datetime.datetime.today().date():
    datum += datetime.timedelta(days=1)
    url = baseurl + datum.strftime("%Y/%m/%d")
    driver.get(url)
    soup = BeautifulSoup(driver.page_source,"html5lib")
    
    for article in soup.findAll("article"):
        scraped_urls.append(article.find("a").get("href"))

# DataFrame aus der bestehenden "urls.csv"-Datei lesen
existing_urls_df = pd.read_csv(r"C:\Users\user00\Documents\GitHub\standard_at_scraping\urls.csv", usecols=["url", "datum", "downloaded"])

# Aktualisierte DataFrame mit neuen Spalten erstellen
new_urls_df = pd.DataFrame({"url": scraped_urls})
new_urls_df["datum"] = datetime.datetime.now().date()  # "Datum" Spalte mit dem heutigen Datum
new_urls_df["downloaded"] = 0  # "Downloaded" Spalte mit 0 initialisieren

# Kombinieren der bestehenden und neuen Daten
combined_urls_df = pd.concat([existing_urls_df, new_urls_df], ignore_index=True)

# CSV-Datei speichern
combined_urls_df.to_csv(r"C:\Users\user00\Documents\GitHub\standard_at_scraping\urls.csv", index=False)
combined_urls_df.to_feather(r"C:\Users\user00\Documents\GitHub\standard_at_scraping\urls.feather")

driver.close()
