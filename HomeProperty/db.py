import sqlite3

def init_db():
    conn = sqlite3.connect('accounts.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            user_type TEXT NOT NULL CHECK(user_type IN ('seller', 'agent')),
            agent_id TEXT UNIQUE DEFAULT NULL,
            phone_number TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

def init_listings_db():
    conn = sqlite3.connect('listings.db')
    c = conn.cursor()

    
    #Now create fresh table with the correct columns
    c.execute('''
        CREATE TABLE listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_username TEXT NOT NULL,
            flat_type TEXT NOT NULL,
            town TEXT NOT NULL,
            street_name TEXT NOT NULL,
            floor_area INTEGER NOT NULL,
            max_com_bid REAL NOT NULL,
            years_remaining INTEGER NOT NULL,
            listing_price REAL NOT NULL,
            bidders TEXT DEFAULT '[]',   -- 2D array of agent bids as JSON
            status TEXT DEFAULT 'A'      -- A = active, B = closed, C = sold
        )
    ''')
    conn.commit()
    conn.close()



def get_accounts_connection():
    conn = sqlite3.connect('accounts.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_listings_connection():
    conn = sqlite3.connect('listings.db')
    conn.row_factory = sqlite3.Row
    return conn
