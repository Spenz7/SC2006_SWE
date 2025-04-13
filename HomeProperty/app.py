from flask import Flask
from db import init_db, init_listings_db
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.api_routes import api_bp
from routes.property_routes import property_bp

# Initialize the app
app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Replace with a secure secret key!

# Register blueprints (modular routes)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(api_bp)
app.register_blueprint(property_bp)

# Initialize databases
#init_db()
#init_listings_db()

# Run the app
if __name__ == '__main__':
    app.run(debug=True)