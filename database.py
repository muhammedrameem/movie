import sqlite3

conn = sqlite3.connect('movies.db')

cursor = conn.cursor()
cursor.execute("DELETE FROM movie")
# cursor.execute('''
# CREATE TABLE IF NOT EXISTS movie (
#     name TEXT,
#     poster TEXT,
#     description TEXT,
#     date TEXT,
#     cast TEXT,
#     rating INTEGER,
#     category TEXT,
#     links TEXT
# )
# ''')


conn.commit()
conn.close()
