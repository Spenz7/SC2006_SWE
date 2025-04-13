from flask import Blueprint, session, redirect, url_for, render_template, flash
import sqlite3

dashboard_bp = Blueprint('dashboard', __name__)

# 🧭 Seller Dashboard
@dashboard_bp.route('/seller_dashboard')
def seller_dashboard():
    if 'username' not in session or session.get('user_type') != 'seller':
        return redirect(url_for('auth.login'))

    conn1 = sqlite3.connect('listings.db')
    conn1.row_factory = sqlite3.Row
    c1 = conn1.cursor()

    conn2 = sqlite3.connect('accounts.db')
    conn2.row_factory = sqlite3.Row
    c2 = conn2.cursor()

    sold_records = c2.execute("SELECT * FROM sold_properties").fetchall()
    sold_properties = []

    for record in sold_records:
        property_id = record['property_id']
        listing = c1.execute("SELECT * FROM listings WHERE id = ?", (property_id,)).fetchone()
        if listing:
            listing_dict = dict(listing)
            listing_dict.update({
                'agent_username': record['agent_username'],
                'seller_username': record['seller_username']
            })
            sold_properties.append(listing_dict)

    conn1.close()
    conn2.close()

    return render_template('seller_dashboard.html', sold_listings=sold_properties, full_name=session.get('full_name'))


# 🧭 Agent Dashboard
@dashboard_bp.route('/agent_dashboard')
def agent_dashboard():
    if 'username' not in session or session.get('user_type') != 'agent':
        flash("Access denied! Only agents can view this page.", "danger")
        return redirect(url_for('auth.login'))

    conn1 = sqlite3.connect('listings.db')
    conn1.row_factory = sqlite3.Row
    c1 = conn1.cursor()

    conn2 = sqlite3.connect('accounts.db')
    conn2.row_factory = sqlite3.Row
    c2 = conn2.cursor()

    sold_records = c2.execute("SELECT * FROM sold_properties").fetchall()
    sold_properties = []

    for record in sold_records:
        property_id = record['property_id']
        listing = c1.execute("SELECT * FROM listings WHERE id = ?", (property_id,)).fetchone()
        if listing:
            listing_dict = dict(listing)
            listing_dict.update({
                'agent_username': record['agent_username'],
                'seller_username': record['seller_username']
            })
            sold_properties.append(listing_dict)

    conn1.close()
    conn2.close()

    return render_template('agent_dashboard.html', sold_listings=sold_properties, full_name=session.get('full_name'))


# 🏠 Homepage
@dashboard_bp.route('/')
def index():
    conn1 = sqlite3.connect('listings.db')
    conn1.row_factory = sqlite3.Row
    c1 = conn1.cursor()

    conn2 = sqlite3.connect('accounts.db')
    conn2.row_factory = sqlite3.Row
    c2 = conn2.cursor()

    sold_records = c2.execute("SELECT * FROM sold_properties").fetchall()
    sold_properties = []

    for record in sold_records:
        property_id = record['property_id']
        agent_username = record['agent_username']
        seller_username = record['seller_username']

        listing = c1.execute("SELECT * FROM listings WHERE id = ?", (property_id,)).fetchone()
        if listing:
            listing_dict = dict(listing)
            listing_dict['agent_username'] = agent_username
            listing_dict['seller_username'] = seller_username
            sold_properties.append(listing_dict)

    conn1.close()
    conn2.close()
    
    return render_template('index.html', sold_listings=sold_properties)