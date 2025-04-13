from flask import Blueprint, session, redirect, url_for, render_template, flash
import sqlite3
import json

dashboard_bp = Blueprint('dashboard', __name__)

# 🧭 Seller Dashboard
@dashboard_bp.route('/seller_dashboard')
def seller_dashboard():
    if 'username' not in session or session.get('user_type') != 'seller':
        return redirect(url_for('auth.login'))

    sold_properties = []

    try:
        conn1 = sqlite3.connect('listings.db')
        conn1.row_factory = sqlite3.Row
        c1 = conn1.cursor()

        conn2 = sqlite3.connect('accounts.db')
        conn2.row_factory = sqlite3.Row
        c2 = conn2.cursor()

        sold_listings = c1.execute("SELECT * FROM listings WHERE status = 'C'").fetchall()

        for listing in sold_listings:
            listing_dict = dict(listing)
            seller_info = c2.execute("SELECT full_name FROM users WHERE username = ?", (listing_dict['seller_username'],)).fetchone()
            listing_dict['seller_username'] = seller_info['full_name'] if seller_info else listing_dict['seller_username']

            bidders = json.loads(listing_dict.get('bidders', '[]'))
            if bidders:
                accepted_bid = bidders[-1]
                agent_username = accepted_bid[0]
                agent_info = c2.execute("SELECT full_name FROM users WHERE username = ?", (agent_username,)).fetchone()
                listing_dict['agent_username'] = agent_info['full_name'] if agent_info else agent_username
            else:
                listing_dict['agent_username'] = "N/A"

            sold_properties.append(listing_dict)

        conn1.close()
        conn2.close()

    except sqlite3.OperationalError as e:
        if 'no such table: listings' in str(e):
            print("⚠️ Table 'listings' not found. Creating it now...")

            try:
                conn = sqlite3.connect('listings.db')
                c = conn.cursor()
                c.execute('''
                    CREATE TABLE IF NOT EXISTS listings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        seller_username TEXT NOT NULL,
                        flat_type TEXT NOT NULL,
                        town TEXT NOT NULL,
                        street_name TEXT NOT NULL,
                        floor_area INTEGER NOT NULL,
                        max_com_bid REAL NOT NULL,
                        years_remaining INTEGER NOT NULL,
                        listing_price REAL NOT NULL,
                        bidders TEXT DEFAULT '[]',
                        status TEXT DEFAULT 'A'
                    )
                ''')
                conn.commit()
                conn.close()
                print("✅ 'listings' table created successfully.")
            except Exception as create_err:
                print(f"❌ Failed to create table: {create_err}")
        else:
            print(f"❌ Unexpected error: {e}")

    return render_template('seller_dashboard.html', sold_listings=sold_properties, full_name=session.get('full_name'))

# 🧭 Agent Dashboard
@dashboard_bp.route('/agent_dashboard')
def agent_dashboard():
    if 'username' not in session or session.get('user_type') != 'agent':
        flash("Access denied! Only agents can view this page.", "danger")
        return redirect(url_for('auth.login'))

    sold_properties = []

    try:
        conn1 = sqlite3.connect('listings.db')
        conn1.row_factory = sqlite3.Row
        c1 = conn1.cursor()

        conn2 = sqlite3.connect('accounts.db')
        conn2.row_factory = sqlite3.Row
        c2 = conn2.cursor()

        sold_listings = c1.execute("SELECT * FROM listings WHERE status = 'C'").fetchall()

        for listing in sold_listings:
            listing_dict = dict(listing)
            seller_info = c2.execute("SELECT full_name FROM users WHERE username = ?", (listing_dict['seller_username'],)).fetchone()
            listing_dict['seller_username'] = seller_info['full_name'] if seller_info else listing_dict['seller_username']

            bidders = json.loads(listing_dict.get('bidders', '[]'))
            if bidders:
                accepted_bid = bidders[-1]
                agent_username = accepted_bid[0]
                agent_info = c2.execute("SELECT full_name FROM users WHERE username = ?", (agent_username,)).fetchone()
                listing_dict['agent_username'] = agent_info['full_name'] if agent_info else agent_username
            else:
                listing_dict['agent_username'] = "N/A"

            sold_properties.append(listing_dict)

        conn1.close()
        conn2.close()

    except sqlite3.OperationalError as e:
        if 'no such table: listings' in str(e):
            print("⚠️ Table 'listings' not found. Creating it now...")

            try:
                conn = sqlite3.connect('listings.db')
                c = conn.cursor()
                c.execute('''
                    CREATE TABLE IF NOT EXISTS listings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        seller_username TEXT NOT NULL,
                        flat_type TEXT NOT NULL,
                        town TEXT NOT NULL,
                        street_name TEXT NOT NULL,
                        floor_area INTEGER NOT NULL,
                        max_com_bid REAL NOT NULL,
                        years_remaining INTEGER NOT NULL,
                        listing_price REAL NOT NULL,
                        bidders TEXT DEFAULT '[]',
                        status TEXT DEFAULT 'A'
                    )
                ''')
                conn.commit()
                conn.close()
                print("✅ 'listings' table created successfully.")
            except Exception as create_err:
                print(f"❌ Failed to create table: {create_err}")
        else:
            print(f"❌ Unexpected error: {e}")
   
    return render_template('agent_dashboard.html', sold_listings=sold_properties, full_name=session.get('full_name'))


# 🏠 Homepage
@dashboard_bp.route('/')
def index():
    sold_properties = []

    try:
        conn1 = sqlite3.connect('listings.db')
        conn1.row_factory = sqlite3.Row
        c1 = conn1.cursor()

        conn2 = sqlite3.connect('accounts.db')
        conn2.row_factory = sqlite3.Row
        c2 = conn2.cursor()

        sold_listings = c1.execute("SELECT * FROM listings WHERE status = 'C'").fetchall()

        for listing in sold_listings:
            listing_dict = dict(listing)
            seller_info = c2.execute("SELECT full_name FROM users WHERE username = ?", (listing_dict['seller_username'],)).fetchone()
            listing_dict['seller_username'] = seller_info['full_name'] if seller_info else listing_dict['seller_username']

            bidders = json.loads(listing_dict.get('bidders', '[]'))
            if bidders:
                accepted_bid = bidders[-1]
                agent_username = accepted_bid[0]
                agent_info = c2.execute("SELECT full_name FROM users WHERE username = ?", (agent_username,)).fetchone()
                listing_dict['agent_username'] = agent_info['full_name'] if agent_info else agent_username
            else:
                listing_dict['agent_username'] = "N/A"

            sold_properties.append(listing_dict)

        conn1.close()
        conn2.close()

    except sqlite3.OperationalError as e:
        if 'no such table: listings' in str(e):
            print("⚠️ Table 'listings' not found. Creating it now...")

            try:
                conn = sqlite3.connect('listings.db')
                c = conn.cursor()
                c.execute('''
                    CREATE TABLE IF NOT EXISTS listings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        seller_username TEXT NOT NULL,
                        flat_type TEXT NOT NULL,
                        town TEXT NOT NULL,
                        street_name TEXT NOT NULL,
                        floor_area INTEGER NOT NULL,
                        max_com_bid REAL NOT NULL,
                        years_remaining INTEGER NOT NULL,
                        listing_price REAL NOT NULL,
                        bidders TEXT DEFAULT '[]',
                        status TEXT DEFAULT 'A'
                    )
                ''')
                conn.commit()
                conn.close()
                print("✅ 'listings' table created successfully.")
            except Exception as create_err:
                print(f"❌ Failed to create table: {create_err}")
        else:
            print(f"❌ Unexpected error: {e}")
        
    return render_template('index.html', sold_listings=sold_properties)