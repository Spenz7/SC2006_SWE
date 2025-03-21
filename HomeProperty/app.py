from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import re
import os
import requests
from twilio.rest import Client #need for SMS OTP
import random
import time

app = Flask(__name__)

#need this to keep track of session
app.secret_key = "your_secret_key_here"

# Database setup (SQLite)
def init_db():
    conn = sqlite3.connect('accounts.db')
    c = conn.cursor()

    # Drop the existing users table if needed (optional)
    c.execute("DROP TABLE IF EXISTS users")

    # Create the users table with phone_number and ensure it's unique
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        user_type TEXT NOT NULL CHECK(user_type IN ('seller', 'agent')),
        agent_id TEXT UNIQUE DEFAULT NULL,  -- Allow NULL for sellers
        phone_number TEXT UNIQUE NOT NULL  -- Ensure no duplicates
        )
    ''')

    conn.commit()
    conn.close()

def init_listings_db():
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
            min_bid_interval REAL NOT NULL,
            years_remaining INTEGER NOT NULL,
            listing_price REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db() #re-run this whenever u wan del existing db
init_listings_db()

import sqlite3
import requests
import time

import requests
import time

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

def find_similar_past_prices(flat_type, town, floor_area, remaining_lease):
    dataset_id = "d_8b84c4ee58e3cfc0ece0d773c8ca6abc"
    base_url = "https://data.gov.sg/api/action/datastore_search"

    min_area = int(floor_area) - 10
    max_area = int(floor_area) + 10
    min_lease = int(remaining_lease) - 5
    max_lease = int(remaining_lease) + 5

    filtered = []

    for offset in range(0, 250000, 1000):
        page_number = (offset // 1000) + 1
        print(f"📦 Fetching records... Page {page_number}, Offset {offset}")
        params = {
            "resource_id": dataset_id,
            "limit": 1000,
            "offset": offset
        }

        try:
            response = requests.get(base_url, params=params)
            data = response.json()

            if "result" not in data or "records" not in data["result"]:
                break

            records = data["result"]["records"]

            for r in records:
                try:
                    area = float(r.get("floor_area_sqm", 0))
                    lease = parse_remaining_lease(r.get("remaining_lease", "0"))
                    resale_price = r.get("resale_price")

                    if (
                        r.get("flat_type") == flat_type and
                        r.get("town") == town and
                        resale_price and
                        min_area <= area <= max_area and
                        min_lease <= lease <= max_lease
                    ):
                        filtered.append(r)
                        if len(filtered) >= 5:
                            break  # Stop inner loop
                except Exception as e:
                    print("⚠️ Skipped record due to error:", e)
                    continue

            if len(filtered) >= 5:
                break  # Stop outer loop

            time.sleep(0.1)
        except Exception as e:
            print(f"❌ Error fetching or parsing data: {e}")
            break

    # Sort by most recent month (in case 5 were not the latest)
    filtered.sort(key=lambda x: x.get("month", ""), reverse=True)

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
    } for r in filtered[:5]]
# Run these functions when initializing the app

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
        
        # Check if phone number already exists
        c.execute("SELECT * FROM users WHERE phone_number=?", (phone_number,))
        if c.fetchone():
            conn.close()
            error_message = "Phone number already in use. Please use a different number."
            return render_template('create_account.html', error_message=error_message)

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

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user-type']  # Get the user type from the form

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
    
    # Database connection
    conn = sqlite3.connect('listings.db')
    conn.row_factory = sqlite3.Row  
    c = conn.cursor()
        
    username = session['username']
    properties = c.execute("SELECT * FROM listings WHERE seller_username = ?", (username,)).fetchall()
    

    return render_template('view_your_property.html',properties=properties)

@app.route('/get_property_details/<int:id>')
def get_property_details(id):
    if 'username' not in session or session.get('user_type') != 'seller':
        return jsonify({'error': 'Unauthorized access'}), 403
    
    conn = sqlite3.connect('listings.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Get property details
    property = c.execute("SELECT * FROM listings WHERE id = ?", (id,)).fetchone()
    
    if not property:
        return jsonify({'error': 'Property not found'}), 404
    
    conn.close()

    # ✅ Hardcoded bidder data for testing
    bidder_data = [
        {'bidder_username': 'PropAgent1', 'bid_amount': 1.5, 'review': '4.5/5'},
        {'bidder_username': 'PropAgent2', 'bid_amount': 1.8, 'review': '5/5'}
        ]
    
    property_data = dict(property)
    
    return jsonify({
        'property': property_data,
        'bidders': bidder_data
    })



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
        min_bid_interval = request.form.get('min_bid_interval')
        years_remaining = request.form.get('years_remaining')
        listing_price = request.form.get('listing_price')

        # Input validation
        try:
            floor_area = int(floor_area)
            min_bid_interval = float(min_bid_interval)
            years_remaining = int(years_remaining)
            listing_price = float(listing_price)

            if floor_area < 1 or min_bid_interval < 0 or min_bid_interval > 3 or years_remaining < 1 or listing_price < 0:
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
        
        """c.execute('''CREATE TABLE IF NOT EXISTS listings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        seller_username TEXT NOT NULL,
                        flat_type TEXT NOT NULL,
                        town TEXT NOT NULL,
                        street_name TEXT NOT NULL,
                        floor_area INTEGER NOT NULL,
                        min_bid_interval REAL NOT NULL,
                        years_remaining INTEGER NOT NULL,
                        listing_price REAL NOT NULL
                    )''')"""
    
        # Insert the property listing
        c.execute("INSERT INTO listings (seller_username, flat_type, town, street_name, floor_area, min_bid_interval, years_remaining, listing_price) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (session['username'], flat_type, town, street_name, floor_area, min_bid_interval, years_remaining, listing_price))

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
        results = find_similar_past_prices(flat_type, town, int(floor_area), int(years_remaining))
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# For Agent Dashbaords.
@app.route('/agent_dashboard')
def agent_dashboard():
    if 'username' not in session or session.get('user_type') != 'agent':
        flash("Access denied! Only agents can view this page.", "danger")
        return redirect(url_for('login'))

    return render_template('agent_dashboard.html', full_name=session.get('full_name'))

@app.route('/view_listed_property') #View Property that have been listed by the Agents available for bidding
def view_listed_property():
    if 'username' not in session or session.get('user_type') != 'agent':
        flash("Access denied! Only agents can view this page.", "danger")
        return redirect(url_for('login'))
    return render_template('view_listed_property.html')

@app.route('/view_bidded_property') #View Properties that you have bidded.
def view_bidded_property():
    if 'username' not in session or session.get('user_type') != 'agent':
        flash("Access denied! Only agents can view this page.", "danger")
        return redirect(url_for('login'))
    return render_template('view_bidded_property.html')


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
    init_listings_db()
    app.run(debug=True)
