import sqlite3
from transformers import BertTokenizer, BertForSequenceClassification
from torch.nn.functional import softmax
import torch

def sentiment_analysis(text, tokenizer, model):
    inputs = tokenizer.encode_plus(text, return_tensors="pt", max_length=128, padding="max_length", truncation=True)
    logits = model(**inputs).logits
    
    # Softmax auf Logits anwenden, um Wahrscheinlichkeiten zu erhalten
    probabilities = softmax(logits, dim=-1)
    
    maximum = torch.max(probabilities).item()
    if maximum == probabilities[0,1]:
        return 1
    elif maximum == probabilities[0,2]:
        return -1
    else:
        return 0

# Verbindung zur SQLite-Datenbank herstellen
conn = sqlite3.connect("article_data.db")
cursor = conn.cursor()

# Versuchen, neue Spalte "Sentiment value" hinzuzufügen, Fehler abfangen, wenn die Spalte bereits existiert
try:
    cursor.execute("ALTER TABLE articles ADD COLUMN `sentiment` REAL")
    conn.commit()
except sqlite3.OperationalError:
    pass


# BERT-Modell für die deutsche Sentiment-Analyse laden
model_name = "oliverguhr/german-sentiment-bert"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name)

# Daten aus der Datenbank abrufen (nur Zeilen, bei denen der Sentiment-Wert fehlt)
cursor.execute("SELECT id, body FROM articles WHERE `sentiment` IS NULL")
rows = cursor.fetchall()

# Sentiment-Analyse für jeden Text in der Datenbank durchführen und Ergebnisse speichern
for i in range(len(rows)):
    print(str(i) + " of "+ str(len(rows))+" set.")
    row = rows[i]
    primary_key, text = row
    sentiment = sentiment_analysis(text, tokenizer, model)
    cursor.execute("UPDATE articles SET sentiment = ? WHERE id = ?", (sentiment, primary_key))
    conn.commit()

conn.close()


