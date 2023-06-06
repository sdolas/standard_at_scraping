import datetime 
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from selenium import webdriver as wd
import sqlite3


# Verbindung zur Datenbank herstellen
# Tabelle erstellen
conn = sqlite3.connect('article_data.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS articles
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              url TEXT,
              kicker TEXT,
              title TEXT,
              subtitle TEXT,
              origins TEXT,
              pubdate TEXT,
              body TEXT)''')

# URL-Daten auslesen
baseurl = r"https://www.derstandard.at"
urls_df = pd.read_csv(r"C:\Users\user00\Documents\GitHub\standard_at_scraping\urls.csv", usecols=["url","downloaded","datum"])

# setze den User Agent
options = Options()
options.add_argument('--user-agent=SimonDolas (contact: sdolas0909@gmail.com)')

# Chrome öffnen
driver = wd.Chrome(r'C:\Users\user00\Documents\selenium webdriver chrome\chromedriver.exe')
driver.set_page_load_timeout(15)

success = False
# erste Seite laden
while not success:
    try:
        # Seite laden
        driver.get(r"https://www.derstandard.at/story/3000000173549/arktisches-meereis-koennte-schon-in-zehn-jahren-saisonal-verschwinden")
    
        # Werbung akzeptieren
        time.sleep(5)
        driver.switch_to.frame(driver.find_element(By.XPATH, "/html/body/div/iframe"))
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div[3]/div[1]/button").click()
        success = True
    except Exception as e:
        print(f"Error: {e}")

# Push-Nachrichten ablehnen
driver.get(r"https://www.derstandard.at/story/3000000173549/arktisches-meereis-koennte-schon-in-zehn-jahren-saisonal-verschwinden")
time.sleep(15)
try:
    driver.find_element(By.XPATH, "/html/body/div[7]/div[3]/div[3]/div[1]/button[1]").click()
except:
    pass

# Scraping der Artikel-Informationen
for i,row in urls_df.iterrows():
    if row["downloaded"] != 0:
        continue
    if baseurl in row["datum"]:
        continue
    url = row["url"]
    
    try:
        # Seite laden und BeautifulSoup-Objekt erstellen
        driver.get(baseurl + url)
        soup = BeautifulSoup(driver.page_source, "html5lib")
        
        # Informationen extrahieren
        kicker = soup.find(class_='article-kicker').text.lstrip()
        title = soup.find(class_='article-title').text.lstrip()
        subtitle = soup.find(class_='article-subtitle').text.lstrip()
        try: 
            origins = soup.find(class_='article-origins').text.strip()
        except AttributeError:
            origins = ""
        pubdate = datetime.datetime.strptime(soup.find('time')['datetime'].strip(), '%Y-%m-%dT%H:%M')
        body = soup.find(class_='article-body').text.strip()

        # Artikel-Informationen in die Datenbank schreiben
        c.execute('''INSERT INTO articles (url, kicker, title, subtitle, origins, pubdate, body)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''', (url, kicker, title, subtitle, origins, pubdate, body))
        conn.commit()
        urls_df["downloaded"].iloc[i] = 1
        print(time.time())

    except Exception as e:
        urls_df["url"] = urls_df["url"][urls_df.url != url]
        urls_df["downloaded"].iloc[i] = 2
        print(f"Error scraping {url}: {e}")
        
# Verbindung zur Datenbank schließen
conn.close()
driver.close()

urls_df.to_feather(r"C:\Users\user00\Documents\GitHub\standard_at_scraping\urls2.feather")
urls_df.to_csv(r"C:\Users\user00\Documents\GitHub\standard_at_scraping\urls2.csv")
