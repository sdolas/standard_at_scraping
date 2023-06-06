import sqlite3

# Erstellen einer SQLite-Datenbank und Verbinden
conn = sqlite3.connect('article_data.db')
cursor = conn.cursor()

# Löschen von Zeilen mit gleichen Werten in den Spalten 'title' und 'subtitle'
cursor.execute('''
DELETE FROM articles
WHERE id IN (
    SELECT MIN(id) 
    FROM articles 
    GROUP BY title, subtitle
    HAVING COUNT(*) > 1
)
''')

conn.commit()

# Löschen von Zeilen mit gleichen Werten in den Spalten 'title' und 'subtitle' (für verbleibende Duplikate)
cursor.execute('''
DELETE FROM articles
WHERE id NOT IN (
    SELECT MIN(id) 
    FROM articles 
    GROUP BY title, subtitle
)
''')

conn.commit()

# Ausgabe der bereinigten Daten
cursor.execute('SELECT * FROM articles')
rows = cursor.fetchall()
for row in rows:
    print(row)

# Schließen der Verbindung
conn.close()
