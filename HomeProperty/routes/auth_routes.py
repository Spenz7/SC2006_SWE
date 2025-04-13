from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import re
from services.otp_service import send_otp_sms, TwilioOTPStrategy
from services.agent_checker import check_agent_id
from utils.validators import is_strong_password
from config import ACCOUNT_SID, AUTH_TOKEN, TWILIO_NUMBER

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/send_otp', methods=['POST'])
def send_otp():
    try:
        data = request.get_json()
        phone_number = data['phone_number'].strip()

        if not phone_number.startswith('+65'):
            return jsonify({'success': False, 'message': 'Phone number must start with +65.'}), 400

        strategy = TwilioOTPStrategy(ACCOUNT_SID, AUTH_TOKEN, TWILIO_NUMBER)
        message_sid = send_otp_sms(phone_number, strategy)
        return jsonify({'success': True, 'message': 'OTP sent successfully.'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@auth_bp.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        form = request.form
        full_name = form['full_name'].strip()
        username = form['username'].strip()
        password = form['password'].strip()
        confirm_password = form['confirm-password'].strip()
        phone_number = form['phone_number'].strip()
        user_type = form['user-type'].strip()
        otp = form.get('otp')

        if password != confirm_password:
            return render_template('create_account.html', error_message="Passwords do not match.")

        if not is_strong_password(password):
            return render_template('create_account.html', error_message="Weak password. Please follow the required format.")

        if not phone_number.startswith('+65'):
            phone_number = '+65' + phone_number

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