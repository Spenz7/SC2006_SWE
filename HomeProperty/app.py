from flask import Flask, render_template, request, redirect, url_for, session, flash
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
    c.execute("DROP TABLE IF EXISTS users")

    # Create the users table with agent_registration_no
    c.execute('''
        CREATE TABLE users (
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


@app.route('/seller_dashboard')
def seller_dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in
    return f"Welcome {session['full_name']}, this is the seller dashboard."

@app.route('/create_listing')
def create_listing():
    return "This is where the seller can create a new listing."

@app.route('/view_listings')
def view_listings():
    return "This is where the seller can view their listings."

@app.route('/agent_dashboard')
def agent_dashboard():
    return render_template('properties.html')#agent-dashboard.html <currently properties.html for placeholder>

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
