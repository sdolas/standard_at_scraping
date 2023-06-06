import datetime
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from selenium import webdriver as wd
import sqlite3


def create_database_connection():
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
    return conn, c


def load_urls_dataframe():
    urls_df = pd.read_feather(r"C:\Users\user00\Documents\GitHub\standard_at_scraping\urls.feather")
    urls_df.dropna(subset=['url'], inplace=True)
    urls_df = urls_df.url.reset_index()
    return urls_df


def remove_existing_urls_from_dataframe(urls_df, c):
    c.execute('SELECT url FROM articles')
    existing_urls = [result[0] for result in c.fetchall()]
    urls_df = urls_df[~urls_df['url'].isin(existing_urls)]
    return urls_df

def set_user_agent():
    options = Options()
    options.add_argument('--user-agent=SimonDolas (contact: sdolas0909@gmail.com)')
    return options

def open_chrome_driver(options):
    driver = wd.Chrome(r'C:\Users\user00\Documents\selenium webdriver chrome\chromedriver.exe', options=options)
    return driver

def accept_advertising(driver, baseurl, urls_df):
    success = False
    while not success:
        try:
            driver.get(baseurl + urls_df.url.iloc[0])
            time.sleep(2)
            driver.switch_to.frame(driver.find_element(By.XPATH, "/html/body/div/iframe"))
            driver.find_element(By.XPATH, "/html/body/div/div[2]/div[3]/div[1]/button").click()
            time.sleep(2)
            success = True
        except Exception as e:
            print(f"Error: {e}")
            urls_df = urls_df.loc[urls_df.url != urls_df.url.iloc[0]]
    return urls_df

def decline_push_notifications(driver, baseurl, urls_df):
    driver.get(baseurl + urls_df.url.iloc[0])
    time.sleep(5)
    try:
        driver.find_element(By.XPATH, "/html/body/div[6]/div[3]/div[3]/div[1]/button[1]").click()
    except:
        pass
    return driver

def scrape_article_information(driver, baseurl, urls_df, c, conn):
    for url in urls_df['url']:
        if baseurl in url:
            continue
        try:
            driver.get(baseurl + url)
            soup = BeautifulSoup(driver.page_source, "html5lib")
            kicker = soup.find(class_='article-kicker').text.lstrip()
            title = soup.find(class_='article-title').text.lstrip()
            subtitle = soup.find(class_='article-subtitle').text.lstrip()
            try:
                origins = soup.find(class_='article-origins').text.strip()
            except AttributeError:
                origins = ""
            pubdate = datetime.datetime.strptime(soup.find('time')['datetime'].strip(), '%Y-%m-%dT%H:%M')
            body = soup.find(class_='article-body').text.strip()

            c.execute('''INSERT INTO articles (url, kicker, title, subtitle, origins, pubdate, body)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''', (url, kicker, title, subtitle, origins, pubdate, body))
            conn.commit()
            print("success")
        except Exception as e:
            urls_df["url"]= urls_df["url"][urls_df.url != url]
            print(f"Error scraping {url}: {e}")
   
    conn.close()
    driver.close()
    pd.DataFrame(urls_df.url).reset_index().to_feather(r"C:\Users\user00\Documents\GitHub\standard_at_scraping\urls.feather")
    
def main():
    baseurl = r"https://www.derstandard.at"
    conn, c = create_database_connection()
    urls_df = load_urls_dataframe()
    urls_df = remove_existing_urls_from_dataframe(urls_df, c)
    options = set_user_agent()
    driver = open_chrome_driver(options)
    urls_df = accept_advertising(driver, baseurl, urls_df)
    driver = decline_push_notifications(driver, baseurl, urls_df)
    scrape_article_information(driver, baseurl, urls_df, c, conn)
    
    
if __name__ == "__main__":
    main()


