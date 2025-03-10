from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import re
import os

app = Flask(__name__)

#need this to keep track of session
app.secret_key = os.urandom(24)

# Database setup (SQLite)
def init_db():
    conn = sqlite3.connect('accounts.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    user_type TEXT NOT NULL
                 )''')
    conn.commit()
    conn.close()

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

# Account creation route
@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user-type']  # Either 'seller' or 'agent'

        # Check if the username already exists in the database
        conn = sqlite3.connect('accounts.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = c.fetchone()  # Fetch one user with the same username
        conn.close()

        if existing_user:
            # If the username exists, display an error message
            error_message = "Username already taken. Please choose another one."
            return render_template('register.html', error_message=error_message)

        # If username doesn't exist, insert the new account into the database
        conn = sqlite3.connect('accounts.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, user_type) VALUES (?, ?, ?)", 
                  (username, password, user_type))
        conn.commit()
        conn.close()

        # Redirect to login page after successful account creation
        return redirect(url_for('login'))

    return render_template('register.html')

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
                  (username, password, user_type))
        user = c.fetchone()  # Fetch one row matching the criteria
        conn.close()

        if user:
            # Successful login, store the username and user_type in session
            session['username'] = username
            session['user_type'] = user_type
            
            # Redirect to the appropriate dashboard
            if user_type == "seller":
                return redirect('/seller_dashboard')  # Redirect to Seller dashboard
            else:
                return redirect('/agent_dashboard')  # Redirect to Agent dashboard
        else:
            # Invalid login, pass an error message back to the template
            error_message = "Invalid credentials or user type. Please try again."
            return render_template('signin.html', error_message=error_message)

    return render_template('signin.html')

@app.route('/logout')
def logout():
    # Remove the user from the session (log out)
    session.pop('username', None)
    session.pop('user_type', None)
    
    # Redirect the user to the login page after logging out
    return redirect(url_for('home'))


@app.route('/seller_dashboard')
def seller_dashboard():
    return render_template('properties-detail.html') #seller-dashboard.html <currently properties-detail for placeholder>

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
def home():
    return render_template('index.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)