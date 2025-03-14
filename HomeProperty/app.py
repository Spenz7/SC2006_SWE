from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import re
import os
import requests

app = Flask(__name__)

#need this to keep track of session
app.secret_key = "your_secret_key_here"

# Database setup (SQLite)
def init_db():
    conn = sqlite3.connect('accounts.db')
    c = conn.cursor()

    # Drop the existing users table if needed (optional)
   # c.execute("DROP TABLE IF EXISTS users")

    # Create the users table with agent_registration_no
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        user_type TEXT NOT NULL CHECK(user_type IN ('seller', 'agent')),
        agent_id TEXT UNIQUE DEFAULT NULL  -- Allow NULL for sellers
        )
    ''')

    conn.commit()
    conn.close()

init_db() #re-run this whenever u wan del existing db

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

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        full_name = request.form['full_name'].strip()
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        user_type = request.form['user-type'].strip()  # Either 'seller' or 'agent'
        
        # Initialize database connection
        conn = sqlite3.connect('accounts.db')
        c = conn.cursor()

        # Check if username already exists
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = c.fetchone()
        if existing_user:
            conn.close()
            error_message = "Username already taken. Please choose another one."
            return render_template('create_account.html', error_message=error_message)

        # Separate handling for agents and sellers
        if user_type == 'seller':
            # Directly insert seller account
            c.execute("INSERT INTO users (full_name, username, password, user_type) VALUES (?, ?, ?, ?)",
                      (full_name, username, password, user_type))
        
        elif user_type == 'agent':
            agent_id = request.form.get('agent_id', '').strip()  # Safely get the agent_id
            
            # Ensure the agent_id is present when the user selects 'agent'
            if not agent_id:
                conn.close()
                error_message = "Agent registration number is required."
                return render_template('create_account.html', error_message=error_message)

            # Validate agent ID against data.gov.sg API
            if not check_agent_id(agent_id):
                conn.close()
                error_message = "Invalid agent registration number. Please enter a valid ID."
                return render_template('create_account.html', error_message=error_message)

            # If valid, insert agent account
            c.execute("INSERT INTO users (full_name, username, password, user_type, agent_id) VALUES (?, ?, ?, ?, ?)",
                      (full_name, username, password, user_type, agent_id))
        
        else:
            conn.close()
            error_message = "Invalid user type selected."
            return render_template('create_account.html', error_message=error_message)

        # Commit changes and close connection
        conn.commit()
        conn.close()

        flash("Account created successfully!", "success")
        return redirect(url_for('login'))

    return render_template('create_account.html')




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
    conn = sqlite3.connect('accounts.db')
    conn.row_factory = sqlite3.Row  
    c = conn.cursor()
        
    username = session['username']
    properties = c.execute("SELECT * FROM listings WHERE seller_username = ?", (username,)).fetchall()
    

    return render_template('view_your_property.html',properties=properties)

@app.route('/get_property_details/<int:id>')
def get_property_details(id):
    if 'username' not in session or session.get('user_type') != 'seller':
        return jsonify({'error': 'Unauthorized access'}), 403
    
    conn = sqlite3.connect('accounts.db')
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

        # Database connection
        conn = sqlite3.connect('accounts.db')
        c = conn.cursor()

        # Create a listings table if it doesn't exist
        c.execute('''CREATE TABLE IF NOT EXISTS listings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        seller_username TEXT NOT NULL,
                        flat_type TEXT NOT NULL,
                        town TEXT NOT NULL,
                        street_name TEXT NOT NULL,
                        floor_area INTEGER NOT NULL,
                        min_bid_interval REAL NOT NULL,
                        years_remaining INTEGER NOT NULL,
                        listing_price REAL NOT NULL
                    )''')

        # Insert the property listing
        c.execute("INSERT INTO listings (seller_username, flat_type, town, street_name, floor_area, min_bid_interval, years_remaining, listing_price) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (session['username'], flat_type, town, street_name, floor_area, min_bid_interval, years_remaining, listing_price))

        conn.commit()
        conn.close()

        flash("Property listed successfully!", "success")
        return redirect(url_for('seller_dashboard'))

    return render_template('list-property.html')





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
    app.run(debug=True)
