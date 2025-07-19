from flask import Flask
from flask_cors import CORS
from database import db
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app, supports_credentials=True)

# セッション管理の設定
app.secret_key = os.getenv('SECRET_KEY', 'tmcit2025-secret-key-change-in-production')
app.config['SESSION_COOKIE_SECURE'] = False  # HTTPSでない場合はFalse
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Create database directory if it doesn't exist
os.makedirs('/data', exist_ok=True)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:////data/attendance.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database with app
db.init_app(app)

# Import models after db initialization
from models import User, Attendance

# Import routes after models
from routes import register_routes
from auth import register_auth_routes

# Create tables and ensure database is initialized
with app.app_context():
    try:
        # This will create the database file if it doesn't exist
        db.create_all()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")

# Register all routes
register_routes(app)
register_auth_routes(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)