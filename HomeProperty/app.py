from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import re
import os
import requests
from twilio.rest import Client #need for SMS OTP
import random
import time
import csv
from werkzeug.security import generate_password_hash

app = Flask(__name__)

#need this to keep track of session
app.secret_key = "your_secret_key_here"

# Database setup (SQLite)
def init_db():
    conn = sqlite3.connect('accounts.db')
    c = conn.cursor()

    # Drop the existing users table if needed (optional)
    #c.execute("DROP TABLE IF EXISTS users")
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='listings'")
    # phone number isn't unique cuz free trial twilio account only allows 1 phone number
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        user_type TEXT NOT NULL CHECK(user_type IN ('seller', 'agent')),
        agent_id TEXT UNIQUE DEFAULT NULL,  -- Allow NULL for sellers
        phone_number TEXT NOT NULL  -- Ensure no duplicates
        )
    ''')

    conn.commit()
    conn.close()

def init_listings_db():
    conn = sqlite3.connect('listings.db')
    c = conn.cursor()

    
    # ✅ Now create fresh table with the correct columns
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

init_db() #re-run this whenever u wan del existing db

def parse_remaining_lease(lease_str):
    try:
        if not lease_str:
            return 0
        parts = lease_str.lower().replace("years", "").replace("year", "").replace("months", "").replace("month", "").split()
        years = int(parts[0]) if len(parts) >= 1 else 0
        months = int(parts[1]) if len(parts) >= 2 else 0
        return round(years + months / 12, 1)
    except:
        return 0

def load_resale_data():
    records = []
    with open('resale_data.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row['floor_area_sqm'] = float(row.get('floor_area_sqm', 0))
            row['resale_price'] = float(row.get('resale_price', 0))
            row['remaining_lease'] = parse_remaining_lease(row.get('remaining_lease', ''))
            records.append(row)
    return sorted(records, key=lambda x: x.get('month', ''), reverse=True)

def filter_records(records, flat_type, town, min_area=None, max_area=None, min_lease=None, max_lease=None):
    result = []
    for r in records:
        if r.get("flat_type") != flat_type or r.get("town") != town:
            continue

        area = r["floor_area_sqm"]
        lease = r["remaining_lease"]

        if min_area is not None and (area < min_area or area > max_area):
            continue
        if min_lease is not None and (lease < min_lease or lease > max_lease):
            continue

        result.append(r)
        if len(result) == 5:
            break
    return result

def find_similar_past_prices(flat_type, town, floor_area, remaining_lease):
    records = load_resale_data()

    # Try strict match first
    results = filter_records(
        records,
        flat_type,
        town,
        min_area=int(floor_area) - 10,
        max_area=int(floor_area) + 10,
        min_lease=int(remaining_lease) - 5,
        max_lease=int(remaining_lease) + 5
    )

    # Fallback #1: match area only, loosened range
    if not results:
        results = filter_records(
            records,
            flat_type,
            town,
            min_area=int(floor_area) - 15,
            max_area=int(floor_area) + 15
        )

    # Fallback #2: match flat_type + town only
    if not results:
        results = filter_records(records, flat_type, town)

    return [{
        "month": r.get("month"),
        "town": r.get("town"),
        "flat_type": r.get("flat_type"),
        "block": r.get("block"),
        "street_name": r.get("street_name"),
        "storey_range": r.get("storey_range"),
        "floor_area_sqm": r.get("floor_area_sqm"),
        "flat_model": r.get("flat_model"),
        "remaining_lease": r.get("remaining_lease"),
        "resale_price": r.get("resale_price")
    } for r in results]
#go to http://localhost:5000/view_accounts to view
@app.route('/view_accounts')
def view_accounts():
    conn = sqlite3.connect('accounts.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users")  # Fetch all accounts
    accounts = c.fetchall()  # Get all results
    conn.close()
    
    # Display the accounts
    return f"Accounts in database: {accounts}"

# Function to check if agent ID exists in data.gov.sg API
def check_agent_id(agent_id):
    dataset_id = "d_07c63be0f37e6e59c07a4ddc2fd87fcb"
    url = f"https://data.gov.sg/api/action/datastore_search?resource_id={dataset_id}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if 'result' in data and 'records' in data['result']:
            records = data['result']['records']
            
            for record in records:
                if record.get('registration_no') == agent_id:
                    return True  # Agent ID found
    except Exception as e:
        print("Error fetching agent data:", e)
    
    return False  # Agent ID not found

# Twilio credentials
account_sid = '***REMOVED***'  # Replace with your Twilio Account SID
auth_token = '***REMOVED***'  # Replace with your Twilio Auth Token
twilio_number = '***REMOVED***'  # Replace with your Twilio phone number

def generate_otp():
    otp = random.randint(100000, 999999)  # Generates a 6-digit OTP
    return otp

# Function to send OTP via SMS using Twilio
def send_otp_sms(phone_number):
    otp = generate_otp()
    
    # Store OTP in session
    session['otp'] = otp
    print("DEBUG: OTP stored in session:", session.get('otp'))  # Add this line to debug

    # Create Twilio client
    client = Client(account_sid, auth_token)
    
    # Send OTP SMS
    message = client.messages.create(
        body=f'Your OTP is {otp}',  # Message body
        from_=twilio_number,  # Your Twilio phone number
        to=phone_number  # The phone number to send OTP to
    )
    
    return message.sid  # Optionally return SID for logging/debugging

@app.route('/send_otp', methods=['POST'])
def send_otp():
    try:
        # Read JSON data
        data = request.get_json()
        phone_number = data['phone_number'].strip()

        # Check if the phone number is valid (starts with +65 for Singapore)
        if not phone_number.startswith('+65'):
            return jsonify({'success': False, 'message': 'Phone number must start with +65.'}), 400

        # Generate OTP and store in session
        otp = generate_otp()
        session['otp'] = otp

        # Send OTP via Twilio
        message_sid = send_otp_sms(phone_number)  # Use the function to send OTP SMS

        # Return a success response
        return jsonify({'success': True, 'message': 'OTP sent successfully.'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

def is_strong_password(password):
    """Check if the password meets strength requirements."""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):  # Check for uppercase letter
        return False
    if not re.search(r'[a-z]', password):  # Check for lowercase letter
        return False
    if not re.search(r'[0-9]', password):  # Check for a digit
        return False
    if not re.search(r'[\W_]', password):  # Check for special character
        return False
    return True


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        full_name = request.form['full_name'].strip()
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        confirm_password = request.form['confirm-password'].strip()
        phone_number = request.form['phone_number'].strip()
        user_type = request.form['user-type'].strip()

        # Validate password match
        if password != confirm_password:
            error_message = "Passwords do not match."
            return render_template('create_account.html', error_message=error_message)
        
        # Validate password strength
        if not is_strong_password(password):
            error_message = "Password must be at least 8 characters long, contain both upper and lower case letters, a number, and a special character."
            return render_template('create_account.html', error_message=error_message)

        # Prepend +65 if not present
        if not phone_number.startswith('+65'):
            phone_number = '+65' + phone_number

        otp = request.form.get('otp')  # Get OTP from form
        print("DEBUG: OTP entered:", otp)  # Add this line to debug
        
        if otp:
            # Ensure OTP is treated as an integer
            otp = int(otp)  # Convert OTP from form to integer
            
            if 'otp' not in session or session['otp'] != otp:
                error_message = "Invalid OTP. Please try again."
                return render_template('create_account.html', error_message=error_message)
            
            del session['otp']  # Clear OTP from session after successful verification

        # Initialize database connection
        conn = sqlite3.connect('accounts.db')
        c = conn.cursor()

        # Check if username already exists
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        if c.fetchone():
            conn.close()
            error_message = "Username already taken. Please choose another one."
            return render_template('create_account.html', error_message=error_message)
        
        # allow duplicate phone number cuz free trial account only allows 1 number
        # # Check if phone number already exists
        # c.execute("SELECT * FROM users WHERE phone_number=?", (phone_number,))
        # if c.fetchone():
        #     conn.close()
        #     error_message = "Phone number already in use. Please use a different number."
        #     return render_template('create_account.html', error_message=error_message)

        # Insert into the database
        if user_type == 'seller':
            c.execute("INSERT INTO users (full_name, username, password, phone_number, user_type) VALUES (?, ?, ?, ?, ?) ",
                      (full_name, username, password, phone_number, user_type))
        
        elif user_type == 'agent':
            agent_id = request.form.get('agent_id', '').strip()
            
            if not agent_id:
                conn.close()
                error_message = "Agent registration number is required."
                return render_template('create_account.html', error_message=error_message)

            if not check_agent_id(agent_id):
                conn.close()
                error_message = "Invalid agent registration number. Please enter a valid ID."
                return render_template('create_account.html', error_message=error_message)

            c.execute("INSERT INTO users (full_name, username, password, phone_number, user_type, agent_id) VALUES (?, ?, ?, ?, ?, ?) ",
                      (full_name, username, password, phone_number, user_type, agent_id))
        
        else:
            conn.close()
            error_message = "Invalid user type selected."
            return render_template('create_account.html', error_message=error_message)

        # Commit changes and close connection
        conn.commit()
        conn.close()

        flash("Account created successfully!", "success")
        return redirect(url_for('login'))  # Redirect to login page after successful account creation

    else:
        # Display the account creation form with OTP field
        phone_number = request.args.get('phone_number')
        return render_template('create_account.html', show_otp=True, phone_number=phone_number)

@app.route('/mark_as_sold', methods=['POST'])
def mark_as_sold():
    if 'username' not in session or session.get('user_type') != 'seller':
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403

    data = request.get_json()
    property_id = data.get('property_id')
    agent_username = data.get('agent_username')
    rating = data.get('rating')
    review = data.get('review')

    if not all([property_id, agent_username, rating]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    try:
        # Update property status in listings.db
        conn1 = sqlite3.connect('listings.db')
        c1 = conn1.cursor()
        c1.execute("UPDATE listings SET status = 'C' WHERE id = ?", (property_id,))
        conn1.commit()
        conn1.close()

        # Insert review into accounts.db
        conn2 = sqlite3.connect('accounts.db')
        c2 = conn2.cursor()
        c2.execute('''
            INSERT INTO sold_properties (property_id, seller_username, agent_username, review_rating, review_text)
            VALUES (?, ?, ?, ?, ?)
        ''', (property_id, session['username'], agent_username, rating, review))
        conn2.commit()
        conn2.close()

        return jsonify({'success': True, 'message': 'Property marked as sold and review saved.'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        username = request.form['username'].strip()
        phone_number = request.form['phone_number'].strip()

        # Ensure phone number starts with +65
        if not phone_number.startswith('+65'):
            phone_number = '+65' + phone_number

        otp = request.form.get('otp')  # OTP entered by the user
        new_password = request.form['new_password'].strip()
        confirm_new_password = request.form['confirm_new_password'].strip()

        # Check if the OTP is correct
        if 'otp' not in session or session['otp'] != int(otp):
            flash("Invalid OTP. Please try again.", "error")
            return redirect(url_for('change_password'))

        # Check if the new password and confirm password match
        if new_password != confirm_new_password:
            flash("Passwords do not match. Please try again.", "error")
            return redirect(url_for('change_password'))

        # Validate password strength
        if not is_strong_password(new_password):
            flash("Password must be at least 8 characters long, contain an uppercase letter, a lowercase letter, a digit, and a special character.", "error")
            return redirect(url_for('change_password'))

        # Validate phone number (check if it matches the user in DB)
        conn = sqlite3.connect('accounts.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND phone_number=?", (username, phone_number))
        user = c.fetchone()
        conn.close()

        if not user:
            flash("User not found or phone number mismatch.", "error")
            return redirect(url_for('change_password'))

        # Store the raw password in the database (no hashing)
        conn = sqlite3.connect('accounts.db')
        c = conn.cursor()
        c.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))
        conn.commit()
        conn.close()

        flash("Password changed successfully!", "success")
        return redirect(url_for('login'))

    return render_template('change_password.html')
    
# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']  # Get the user type from the form

        # Check if the user exists in the database with the selected user_type
        conn = sqlite3.connect('accounts.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=? AND user_type=?", 
          (username.strip(), password.strip(), user_type.strip()))
        user = c.fetchone()  # Fetch one row matching the criteria
        conn.close()

        if user:
            session['username'] = username
            session['user_type'] = user_type
            session['full_name'] = user[1]
            
            print("DEBUG: Session values:", session)  # Debugging statement
            
            if user_type == "seller":
                return redirect('/seller_dashboard')
            else:
                return redirect('/agent_dashboard')
        else:
            # Invalid login, pass an error message back to the template
            error_message = "Either Invalid credentials or account doesn't exist. Please try again."
            return render_template('login.html', error_message=error_message)

    return render_template('login.html')

@app.route('/logout')
def logout():
    # Remove the user from the session (log out)
    session.pop('username', None)
    session.pop('user_type', None)
    
    # Redirect the user to the login page after logging out
    return redirect(url_for('index'))    

@app.route("/test_prices")
def test_prices():
    results = find_similar_past_prices("3 ROOM", "ANG MO KIO", 67, 62)
    return jsonify(results)
 # For Seller dashboards
@app.route('/seller_dashboard')
def seller_dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in

    return render_template('seller_dashboard.html', full_name=session.get('full_name'))

# View Sellers own Properties (Seller)
@app.route('/view_your_property')
def view_your_property():
    if 'username' not in session or session.get('user_type') != 'seller':
        flash("Access denied!", "danger")
        return redirect(url_for('login'))

    username = session['username']

    try:
        # Connect to the database
        conn = sqlite3.connect('listings.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        # Check if 'listings' table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='listings'")
        if not c.fetchone():
            flash("No properties have been listed yet. Please list a property first.", "warning")
            return redirect(url_for('list_property'))

        # Fetch seller's properties
        properties = c.execute("SELECT * FROM listings WHERE seller_username = ?", (username,)).fetchall()
        return render_template('view_your_property.html', properties=properties)

    except Exception as e:
        flash(f"An unexpected error occurred: {str(e)}", "danger")
        return redirect(url_for('seller_dashboard'))

    finally:
        conn.close()

import json

@app.route('/get_property_details/<int:id>')
def get_property_details(id):
    if 'username' not in session or session.get('user_type') != 'seller':
        return jsonify({'error': 'Unauthorized access'}), 403
  
    conn = sqlite3.connect('listings.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    property = c.execute("SELECT * FROM listings WHERE id = ?", (id,)).fetchone()
    if not property:
        conn.close()
        return jsonify({'error': 'Property not found'}), 404

    property_data = dict(property)

    try:
        # ✅ Parse and convert bidders into dictionaries
        raw_bidders = json.loads(property_data.get('bidders', '[]'))
        bidders = [{"agent_username": b[0], "bid_percent": b[1]} for b in raw_bidders]
    except Exception as e:
        print("❌ Error parsing bidders JSON:", e)
        bidders = []

    conn.close()
    print("📦 Returning property details:", property_data)
    print("👥 Returning bidders:", bidders)
    
    response = {
    'property': property_data,
    'bidders': bidders
    }   
    print("🔄 FINAL RESPONSE TO FRONTEND:", response)
    return jsonify(response)
    
@app.route('/submit_bid', methods=['POST'])
def submit_bid():
    if 'username' not in session or session.get('user_type') != 'agent':
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403

    data = request.get_json()
    property_id = data.get('property_id')
    commission = data.get('commission')

    if not property_id or commission is None:
        return jsonify({'success': False, 'message': 'Missing property ID or commission value'}), 400

    try:
        commission = round(float(commission), 2)
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid commission value'}), 400

    conn = sqlite3.connect('listings.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Fetch listing
    listing = c.execute("SELECT * FROM listings WHERE id = ?", (property_id,)).fetchone()
    if not listing:
        conn.close()
        return jsonify({'success': False, 'message': 'Listing not found'}), 404

    if listing['status'] != 'A':
        conn.close()
        return jsonify({'success': False, 'message': 'Bidding is closed for this listing'}), 400

    max_com = listing['max_com_bid']
    if commission > max_com:
        conn.close()
        return jsonify({'success': False, 'message': f'Commission exceeds maximum allowed ({max_com}%)'}), 400

    import json
    try:
        bidders = json.loads(listing['bidders']) if listing['bidders'] else []
    except Exception as e:
        print("❌ Failed to parse bidders JSON:", e)
        bidders = []

    agent_username = session['username']
    # Check if this agent has already bid — update if yes, else append
    for bid in bidders:
        if bid[0] == agent_username:
            bid[1] = commission  # update existing bid
            break
    else:
        bidders.append([agent_username, commission])  # new bid

    # Save updated bidders back to DB
    c.execute("UPDATE listings SET bidders = ? WHERE id = ?", (json.dumps(bidders), property_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Bid submitted successfully!'})

@app.route('/accept_bid', methods=['POST'])
def accept_bid():
    if 'username' not in session or session.get('user_type') != 'seller':
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    property_id = data.get('property_id')
    accepted_agent = data.get('agent_username')

    if not property_id or not accepted_agent:
        return jsonify({'error': 'Missing data'}), 400

    conn = sqlite3.connect('listings.db')
    c = conn.cursor()

    # Fetch the listing
    c.execute("SELECT * FROM listings WHERE id = ?", (property_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Property not found'}), 404

    # Set listing status to 'C' (sold)
    c.execute("UPDATE listings SET status = 'C' WHERE id = ?", (property_id,))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': f"Bid by {accepted_agent} accepted. Listing marked as sold."})


@app.route('/list-property', methods=['GET', 'POST'])
def list_property():
    if 'username' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in

    if session.get('user_type') != 'seller':
        flash("Only sellers can list properties!", "danger")
        return redirect(url_for('index'))  # Redirect unauthorized users

        similar_houses = []

    if request.method == 'POST':
        # Extract form data
        flat_type = request.form.get('flat_type')
        town = request.form.get('town')
        street_name = request.form.get('street_name')
        floor_area = request.form.get('floor_area')
        max_com_bid = request.form.get('max_com_bid')
        years_remaining = request.form.get('years_remaining')
        listing_price = request.form.get('listing_price')

        # Input validation
        try:
            floor_area = int(floor_area)
            max_com_bid = float(max_com_bid)
            years_remaining = int(years_remaining)
            listing_price = float(listing_price)

            if floor_area < 1 or max_com_bid < 0 or max_com_bid > 5 or years_remaining < 1 or listing_price < 0:
                flash("Invalid input values!", "danger")
                return redirect(url_for('list_property'))
        except ValueError:
            flash("Please enter valid numerical values.", "danger")
            return redirect(url_for('list_property'))


        similar_houses = find_similar_past_prices(flat_type, town, floor_area, years_remaining)
        if not similar_houses:
            flash("⚠ No exact matches found. Showing similar listings.", "warning")
                
        # Database connection
        conn = sqlite3.connect('listings.db')
        c = conn.cursor()

        # Create a listings table if it doesn't exist
       # Commenting out table creation since listings.db is already set up
        
    
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
            bidders TEXT DEFAULT '[]',   -- 2D array of agent bids as JSON
            status TEXT DEFAULT 'A'      -- A = active, B = closed, C = sold
        )
    ''')
    
        # Insert the property listing
        c.execute("INSERT INTO listings (seller_username, flat_type, town, street_name, floor_area, max_com_bid, years_remaining, listing_price, bidders, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
          (session['username'], flat_type, town, street_name, floor_area, max_com_bid, years_remaining, listing_price, '[]', 'A'))

        conn.commit()
        conn.close()

        flash("Property listed successfully!", "success")
        return redirect(url_for('seller_dashboard'))

    return render_template('list-property.html')



@app.route('/get_similar_prices')
def get_similar_prices():
    flat_type = request.args.get("flat_type")
    town = request.args.get("town")
    floor_area = request.args.get("floor_area")
    years_remaining = request.args.get("years_remaining")

    if not all([flat_type, town, floor_area, years_remaining]):
        return jsonify({"error": "Missing parameters"}), 400

    try:
        print("🔍 Params received:", flat_type, town, floor_area, years_remaining)
        results = find_similar_past_prices(flat_type, town, int(floor_area), int(years_remaining))
        print("✅ Matching results:", results)
        return jsonify(results)
    except Exception as e:
        print("❌ Error in get_similar_prices:", e)
        return jsonify({"error": str(e)}), 500

# For Agent Dashbaords.
@app.route('/agent_dashboard')
def agent_dashboard():
    if 'username' not in session or session.get('user_type') != 'agent':
        flash("Access denied! Only agents can view this page.", "danger")
        return redirect(url_for('login'))

    return render_template('agent_dashboard.html', full_name=session.get('full_name'))

@app.route('/view_listed_property')
def view_listed_property():
    if 'username' not in session or session.get('user_type') != 'agent':
        flash("Access denied! Only agents can view this page.", "danger")
        return redirect(url_for('login'))

    conn = sqlite3.connect('listings.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    listings = c.execute("SELECT * FROM listings").fetchall()
    final_listings = []

    for listing in listings:
        listing_dict = dict(listing)
        try:
            import json
            bidders = json.loads(listing['bidders']) if listing['bidders'] else []
            # Get the minimum bid value
            if bidders:
                lowest_bid = min(bid[1] for bid in bidders)
            else:
                lowest_bid = None
        except Exception as e:
            print("Error parsing bidders:", e)
            lowest_bid = None

        listing_dict['lowest_bid'] = lowest_bid
        final_listings.append(listing_dict)

    conn.close()
    return render_template('bidding.html', listings=final_listings)

@app.route('/agent_profile/<username>')
def agent_profile(username):
    conn = sqlite3.connect('accounts.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    agent = c.execute("SELECT * FROM users WHERE username = ? AND user_type = 'agent'", (username,)).fetchone()
    if not agent:
        conn.close()
        return "Agent not found", 404

    reviews = c.execute('''
        SELECT * FROM sold_properties
        WHERE agent_username = ?
    ''', (username,)).fetchall()

    conn.close()
    return render_template('agent_profile.html', agent=agent, reviews=reviews)


@app.route('/view_bidded_property')
def view_bidded_property():
    if 'username' not in session or session.get('user_type') != 'agent':
        flash("Access denied! Only agents can view this page.", "danger")
        return redirect(url_for('login'))

    agent_username = session['username']

    conn = sqlite3.connect('listings.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    all_listings = c.execute("SELECT * FROM listings").fetchall()
    conn.close()

    bidded_listings = []

    import json
    for listing in all_listings:
        try:
            bidders = json.loads(listing['bidders'])
            lowest_bid = min([bid[1] for bid in bidders]) if bidders else None

            for bidder in bidders:
                if bidder[0] == agent_username:
                    # Attach bid percent to listing for easy access in template
                    listing_dict = dict(listing)
                    listing_dict['your_bid'] = bidder[1]
                    listing_dict['lowest_bid'] = lowest_bid
                    bidded_listings.append(listing_dict)
                    break
        except Exception as e:
            print("Error parsing bidders JSON:", e)

    return render_template('view_bidded_property.html', listings=bidded_listings)



#unused
@app.route('/404')
def error_page():
    return render_template('404.html')
    
@app.route('/blog-archive')
def blog_archive():
    return render_template('blog-archive.html')
@app.route('/blog-single')
def blog_single():
    return render_template('/blog-single.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

# Home route with buttons
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
