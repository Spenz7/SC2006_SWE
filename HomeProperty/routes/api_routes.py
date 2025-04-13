from flask import Blueprint, request, jsonify, session
import sqlite3
import json
from services.resale_price_service import find_similar_past_prices  # ✅ updated import

api_bp = Blueprint('api', __name__)


@api_bp.route('/get_similar_prices')
def get_similar_prices():
    try:
        flat_type = request.args.get('flat_type')
        town = request.args.get('town')
        floor_area = float(request.args.get('floor_area'))
        years_remaining = float(request.args.get('years_remaining'))

        # ✅ Call the function directly (no service instance)
        results = find_similar_past_prices(flat_type, town, floor_area, years_remaining)

        print("🔁 FINAL 5 RESULTS TO RETURN:")
        for i, r in enumerate(results, start=1):
            print(f"{i}. {r}")

        return jsonify(results)

    except Exception as e:
        print(f"❌ Error in get_similar_prices: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@api_bp.route('/get_property_details/<int:id>')
def get_property_details(id):
    if 'username' not in session or session.get('user_type') != 'seller':
        return jsonify({'error': 'Unauthorized access'}), 403

    conn = sqlite3.connect('listings.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    property = c.execute("SELECT * FROM listings WHERE id = ?", (id,)).fetchone()
    conn.close()

    if not property:
        return jsonify({'error': 'Property not found'}), 404

    property_data = dict(property)

    try:
        raw_bidders = json.loads(property_data.get('bidders', '[]'))
        bidders = [{"agent_username": b[0], "bid_percent": b[1]} for b in raw_bidders]
    except Exception as e:
        print("❌ Error parsing bidders JSON:", e)
        bidders = []

    response = {
        'property': property_data,
        'bidders': bidders
    }

    print("📦 Returning property details:", property_data)
    print("👥 Returning bidders:", bidders)
    return jsonify(response)