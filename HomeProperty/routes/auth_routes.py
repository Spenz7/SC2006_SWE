from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import re
from services.otp_service import send_otp_sms, TwilioOTPStrategy
from services.agent_checker import check_agent_id
from utils.validators import *
from config import ACCOUNT_SID, AUTH_TOKEN, TWILIO_NUMBER

auth_bp = Blueprint('auth', __name__)

#go to http://localhost:5000/view_accounts to view
@auth_bp.route('/view_accounts')
def view_accounts():
    conn = sqlite3.connect('accounts.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users")  # Fetch all accounts
    accounts = c.fetchall()  # Get all results
    conn.close()
    
    # Display the accounts
    return f"Accounts in database: {accounts}"

@auth_bp.route('/send_otp', methods=['POST'])
def send_otp():
    try:
        data = request.get_json(force=True)

        if not data or 'phone_number' not in data:
            return jsonify({'success': False, 'message': 'Missing phone number in request.'}), 400

        phone_number = data['phone_number'].strip()

        # Normalize: remove +65 if present
        if phone_number.startswith('+65'):
            phone_number = phone_number[3:]

        # Validate: must be 8 digits and start with 6, 8, or 9
        if not is_valid_sg_number(phone_number):
            return jsonify({'success': False, 'message': 'Invalid Singapore phone number format.'}), 400

        # Add back the prefix
        phone_number = '+65' + phone_number

        # Send OTP
        strategy = TwilioOTPStrategy(ACCOUNT_SID, AUTH_TOKEN, TWILIO_NUMBER)
        message_sid = send_otp_sms(phone_number, strategy)

        return jsonify({'success': True, 'message': 'OTP sent successfully.'})

    except Exception as e:
        # Catch any internal server errors and return JSON
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@auth_bp.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        form = request.form
        full_name = form['full_name'].strip()
        username = form['username'].strip()
        password = form['password'].strip()
        confirm_password = form['confirm-password'].strip()
        phone_number = form['phone_number'].strip()

        
        # Normalize phone number by removing +65 if present
        if phone_number.startswith('+65'):
            phone_number = phone_number[3:]

        # Validate number format (must be SG and 8 digits starting with 6, 8, or 9)
        if not is_valid_sg_number(phone_number):
            return render_template('create_account.html', error_message="Invalid Singapore phone number format.")

        # Add +65 back
        phone_number = '+65' + phone_number

        user_type = form['user-type'].strip()
        otp = form.get('otp')

        if password != confirm_password:
            return render_template('create_account.html', error_message="Passwords do not match.")

        if not is_strong_password(password):
            return render_template('create_account.html', error_message="Weak password. Please follow the required format.")


        if otp:
            if 'otp' not in session or session['otp'] != int(otp):
                return render_template('create_account.html', error_message="Invalid OTP.")
            del session['otp']

        conn = sqlite3.connect('accounts.db')
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=?", (username,))
        if c.fetchone():
            conn.close()
            return render_template('create_account.html', error_message="Username already taken.")

        if user_type == 'agent':
            agent_id = form.get('agent_id', '').strip()
            if not agent_id:
                conn.close()

            # NEW: check for duplicate agent ID
            c.execute("SELECT * FROM users WHERE agent_id=?", (agent_id,))
            if c.fetchone():
                conn.close()
                return render_template('create_account.html', error_message="Agent ID already in use.")

                return render_template('create_account.html', error_message="Agent ID is required.")
            if not check_agent_id(agent_id):
                conn.close()
                return render_template('create_account.html', error_message="Invalid agent registration number.")

            c.execute("INSERT INTO users (full_name, username, password, phone_number, user_type, agent_id) VALUES (?, ?, ?, ?, ?, ?)",
                      (full_name, username, password, phone_number, user_type, agent_id))
        else:
            c.execute("INSERT INTO users (full_name, username, password, phone_number, user_type) VALUES (?, ?, ?, ?, ?)",
                      (full_name, username, password, phone_number, user_type))

        conn.commit()
        conn.close()
        flash("Account created successfully!", "success")
        return redirect(url_for('auth.login'))

    phone_number = request.args.get('phone_number')
    return render_template('create_account.html', show_otp=True, phone_number=phone_number)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        user_type = request.form['user_type'].strip()

        conn = sqlite3.connect('accounts.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=? AND user_type=?", 
                  (username, password, user_type))
        user = c.fetchone()
        conn.close()

        if user:
            session['username'] = username
            session['user_type'] = user_type
            session['full_name'] = user[1]
            return redirect('/seller_dashboard' if user_type == 'seller' else '/agent_dashboard')

        return render_template('login.html', error_message="Invalid credentials or account does not exist.")

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('dashboard.index'))

@auth_bp.route('/change_password', methods=['GET', 'POST'])
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
            return redirect(url_for('auth.change_password'))

        # Check if the new password and confirm password match
        if new_password != confirm_new_password:
            flash("Passwords do not match. Please try again.", "error")
            return redirect(url_for('auth.change_password'))

        # Validate password strength
        if not is_strong_password(new_password):
            flash("Password must be at least 8 characters long, contain an uppercase letter, a lowercase letter, a digit, and a special character.", "error")
            return redirect(url_for('auth.change_password'))

        # Validate phone number (check if it matches the user in DB)
        conn = sqlite3.connect('accounts.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND phone_number=?", (username, phone_number))
        user = c.fetchone()
        conn.close()

        if not user:
            flash("User not found or phone number mismatch.", "error")
            return redirect(url_for('auth.change_password'))

        # Store the raw password in the database (no hashing)
        conn = sqlite3.connect('accounts.db')
        c = conn.cursor()
        c.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))
        conn.commit()
        conn.close()

        flash("Password changed successfully!", "success")
        return redirect(url_for('auth.login'))

    return render_template('change_password.html')
