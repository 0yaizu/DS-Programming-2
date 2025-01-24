import sqlite3

conn = sqlite3.connect('rent_prices.db')
cur = conn.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS rent_prices(city TEXT, rent_price INTEGER)')

cur.execute('INSERT INTO rent_prices VALUES ("葛飾区", 7)')

conn.commit()
conn.close()