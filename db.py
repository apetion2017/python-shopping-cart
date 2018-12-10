import sqlite3

#Open database
conn = sqlite3.connect('db.db')

conn.execute('''CREATE TABLE products
		(productId INTEGER PRIMARY KEY,
		name TEXT,
		price REAL,
		description TEXT,
		image TEXT,
		stock INTEGER,
		categoryId INTEGER,
		FOREIGN KEY(categoryId) REFERENCES categories(categoryId)
		)''')

conn.execute('''CREATE TABLE kart
		(productId INTEGER,
		FOREIGN KEY(productId) REFERENCES products(productId)
		)''')

conn.execute('''CREATE TABLE categories
		(categoryId INTEGER PRIMARY KEY,
		name TEXT
		)''')
