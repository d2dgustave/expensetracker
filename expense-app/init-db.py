# init_db.py
import sqlite3

connection = sqlite3.connect('expense.db')
with open('schema.sql') as f:
    connection.executescript(f.read())
connection.close()
