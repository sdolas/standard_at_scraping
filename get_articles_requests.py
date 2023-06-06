import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import sqlite3
import random

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

# Alle URLs entfernen, die liveticker sind
urls_list = [x for x in urls_df["url"] if baseurl not in x]

# Liste von User-Agent-Strings
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134'
]

# Scraping der Artikel-Informationen
for url in urls_list:
    try:
        # Seite laden und BeautifulSoup-Objekt erstellen
        headers = {'User-Agent': random.choice(user_agents)}
        response = requests.get(baseurl + url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html5lib")

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

pd.DataFrame(urls_df.url).reset_index().to_feather(r"C:\Users\user00\Documents\GitHub\standard_at_scraping\urls.feather")

