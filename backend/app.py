from flask import Flask
from flask_cors import CORS
from database import db
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:////data/attendance.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database with app
db.init_app(app)

# Import models after db initialization
from models import User, Attendance

# Import routes after models
from routes import register_routes

# Create database directory if it doesn't exist
os.makedirs('/data', exist_ok=True)

# Create tables
with app.app_context():
    db.create_all()

# Register all routes
register_routes(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)