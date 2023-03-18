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
urls_df = pd.read_feather(r"C:\Users\user00\Documents\GitHub\standard_at_scraping\urls.feather")
urls_df.dropna(subset=['url'], inplace=True)
urls_df = urls_df.url.reset_index()

# Alle URLs aus der Datenbank entfernen, die bereits gescraped wurden
c.execute('SELECT url FROM articles')
existing_urls = [result[0] for result in c.fetchall()]
urls_df = urls_df[~urls_df['url'].isin(existing_urls)]

# setze den User Agent
options = Options()
options.add_argument('--user-agent=SimonDolas (contact: sdolas0909@gmail.com)')

# Chrome öffnen
driver = wd.Chrome(r'C:\Users\user00\Documents\selenium webdriver chrome\chromedriver.exe')

success = False
# erste Seite laden
while not success:
    try:
        driver.get(baseurl + urls_df.url.iloc[0])
    
        # Werbung akzeptieren
        time.sleep(5)
        driver.switch_to.frame(driver.find_element(By.XPATH, "/html/body/div/iframe"))
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div[3]/div[1]/button").click()
        time.sleep(15)
        success = True
    except Exception as e:
        print(f"Error: {e}")
        urls_df = urls_df.loc[urls_df.url != urls_df.url.iloc[0]]
    

# Push-Nachrichten ablehnen
driver.find_element(By.XPATH, "/html/body/div[6]/div[3]/div[3]/div[1]/button[1]").click()

# Scraping der Artikel-Informationen
for url in urls_df['url']:
    try:
        # Seite laden und BeautifulSoup-Objekt erstellen
        driver.get(baseurl+url)
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
        print(time.time())

    except Exception as e:
        urls_df["url"] = urls_df["url"][urls_df.url != url]
        print(f"Error scraping {url}: {e}")
        
# Verbindung zur Datenbank schließen
conn.close()
driver.close()

pd.DataFrame(urls_df.url).reset_index().to_feather(r"C:\Users\user00\Documents\GitHub\standard_at_scraping\urls.feather")


