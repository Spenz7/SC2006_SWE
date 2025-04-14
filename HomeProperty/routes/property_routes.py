from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
import json

property_bp = Blueprint('property', __name__)

# List a new property
@property_bp.route('/list-property', methods=['GET', 'POST'])
def list_property():
    if 'username' not in session or session.get('user_type') != 'seller':
        flash("Only sellers can list properties!", "danger")
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        flat_type = request.form.get('flat_type')
        town = request.form.get('town')
        street_name = request.form.get('street_name')
        floor_area = request.form.get('floor_area')
        max_com_bid = request.form.get('max_com_bid')
        years_remaining = request.form.get('years_remaining')
        listing_price = request.form.get('listing_price')

        try:
            floor_area = int(floor_area)
            max_com_bid = float(max_com_bid)
            years_remaining = int(years_remaining)
            listing_price = float(listing_price)

            if floor_area < 1 or max_com_bid < 0 or max_com_bid > 5 or years_remaining < 1 or listing_price < 0:
                flash("Invalid input values!", "danger")
                return redirect(url_for('property.list_property'))
        except ValueError:
            flash("Please enter valid numerical values.", "danger")
            return redirect(url_for('property.list_property'))

        conn = sqlite3.connect('listings.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO listings (
                seller_username, flat_type, town, street_name, floor_area,
                max_com_bid, years_remaining, listing_price, bidders, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session['username'], flat_type, town, street_name, floor_area,
            max_com_bid, years_remaining, listing_price, '[]', 'A'
        ))
        conn.commit()
        conn.close()

        flash("Property listed successfully!", "success")
        return redirect(url_for('property.view_your_property'))

    return render_template('list-property.html')

@property_bp.route('/view_your_property')
def view_your_property():
    if 'username' not in session or session.get('user_type') != 'seller':
        flash("Access denied!", "danger")
        return redirect(url_for('login'))

    username = session['username']
    page = int(request.args.get('page', 1))  # Get current page from query param
    per_page = 15

    try:
        conn = sqlite3.connect('listings.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute("SELECT COUNT(*) FROM listings WHERE seller_username = ?", (username,))
        total_properties = c.fetchone()[0]

        offset = (page - 1) * per_page
        properties = c.execute("""
            SELECT * FROM listings
            WHERE seller_username = ?
            ORDER BY id DESC
            LIMIT ? OFFSET ?
        """, (username, per_page, offset)).fetchall()

        total_pages = (total_properties + per_page - 1) // per_page  # Ceiling division

        return render_template('view_your_property.html',
                               properties=properties,
                               page=page,
                               total_pages=total_pages)

    except Exception as e:
        flash(f"An unexpected error occurred: {str(e)}", "danger")
        return redirect(url_for('seller_dashboard'))

    finally:
        conn.close()


@property_bp.route('/agent_profile/<username>')
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

# Submit a bid by agent
@property_bp.route('/submit_bid', methods=['POST'])
def submit_bid():
    if 'username' not in session or session.get('user_type') != 'agent':
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403

    data = request.get_json()
    property_id = data.get('property_id')
    commission = data.get('commission')

    if not property_id or commission is None:
        return jsonify({'success': False, 'message': 'Missing data'}), 400

    try:
        commission = round(float(commission), 2)
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid commission value'}), 400

    conn = sqlite3.connect('listings.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    listing = c.execute("SELECT * FROM listings WHERE id = ?", (property_id,)).fetchone()

    if not listing:
        conn.close()
        return jsonify({'success': False, 'message': 'Listing not found'}), 404

    if listing['status'] != 'A':
        conn.close()
        return jsonify({'success': False, 'message': 'Bidding is closed'}), 400

    max_com = listing['max_com_bid']
    if commission > max_com:
        conn.close()
        return jsonify({'success': False, 'message': f'Commission exceeds max allowed ({max_com}%)'}), 400

    try:
        bidders = json.loads(listing['bidders']) if listing['bidders'] else []
    except Exception as e:
        print("❌ Failed to parse bidders JSON:", e)
        bidders = []

    agent_username = session['username']
    for bid in bidders:
        if bid[0] == agent_username:
            bid[1] = commission
            break
    else:
        bidders.append([agent_username, commission])

    c.execute("UPDATE listings SET bidders = ? WHERE id = ?", (json.dumps(bidders), property_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Bid submitted successfully!'})

@property_bp.route('/view_bidded_property')
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

@property_bp.route('/view_listed_property')
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


# Accept a bid by seller
@property_bp.route('/accept_bid', methods=['POST'])
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
    c.execute("UPDATE listings SET status = 'C' WHERE id = ?", (property_id,))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': f"Bid by {accepted_agent} accepted. Listing marked as sold.",'redirect': '/view_your_property'})


# Mark a property as sold with review
@property_bp.route('/mark_as_sold', methods=['POST'])
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
        conn1 = sqlite3.connect('listings.db')
        c1 = conn1.cursor()
        c1.execute("UPDATE listings SET status = 'C' WHERE id = ?", (property_id,))
        conn1.commit()
        conn1.close()

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
    

# Update listing details (price, max commission, years remaining)
@property_bp.route('/update_listing', methods=['POST'])
def update_listing():
    if 'username' not in session or session.get('user_type') != 'seller':
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403

    data = request.get_json()
    property_id = data.get('property_id')
    listing_price = data.get('listing_price')
    max_com_bid = data.get('max_com_bid')
    years_remaining = data.get('years_remaining')

    if not all([property_id, listing_price, max_com_bid, years_remaining]):
        return jsonify({'success': False, 'message': 'Missing fields'}), 400

    try:
        conn = sqlite3.connect('listings.db')
        c = conn.cursor()
        c.execute('''
            UPDATE listings
            SET listing_price = ?, max_com_bid = ?, years_remaining = ?
            WHERE id = ? AND seller_username = ?
        ''', (listing_price, max_com_bid, years_remaining, property_id, session['username']))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Listing updated successfully.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@property_bp.route('/delete_listing/<int:property_id>', methods=['DELETE'])
def delete_listing(property_id):
    if 'username' not in session or session.get('user_type') != 'seller':
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403

    username = session['username']

    try:
        conn = sqlite3.connect('listings.db')
        c = conn.cursor()
        c.execute("DELETE FROM listings WHERE id = ? AND seller_username = ?", (property_id, username))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Listing deleted successfully.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
