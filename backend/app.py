from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import bcrypt
import qrcode
import io
import base64
from datetime import datetime, date
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    check_in = db.Column(db.DateTime)
    check_out = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('attendances', lazy=True))

# Auth Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    user = User(username=username, email=email)
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 200
    
    return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email
    }), 200

# QR Code Generation
@app.route('/api/generate-qr', methods=['POST'])
@jwt_required()
def generate_qr():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    target_date = data.get('date', str(date.today()))
    
    # QR Code data: username and date
    qr_data = f"{user.username}:{target_date}"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create PIL image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode()
    
    return jsonify({
        'qr_code': f"data:image/png;base64,{img_base64}",
        'data': qr_data,
        'date': target_date
    }), 200

# Attendance Routes
@app.route('/api/check-in', methods=['POST'])
@jwt_required()
def check_in():
    user_id = get_jwt_identity()
    today = date.today()
    
    existing_attendance = Attendance.query.filter_by(
        user_id=user_id, 
        date=today
    ).first()
    
    if existing_attendance and existing_attendance.check_in:
        return jsonify({'error': 'Already checked in today'}), 400
    
    if existing_attendance:
        existing_attendance.check_in = datetime.now()
    else:
        attendance = Attendance(
            user_id=user_id,
            date=today,
            check_in=datetime.now()
        )
        db.session.add(attendance)
    
    db.session.commit()
    return jsonify({'message': 'Checked in successfully'}), 200

@app.route('/api/check-out', methods=['POST'])
@jwt_required()
def check_out():
    user_id = get_jwt_identity()
    today = date.today()
    
    attendance = Attendance.query.filter_by(
        user_id=user_id, 
        date=today
    ).first()
    
    if not attendance or not attendance.check_in:
        return jsonify({'error': 'No check-in record found'}), 400
    
    if attendance.check_out:
        return jsonify({'error': 'Already checked out today'}), 400
    
    attendance.check_out = datetime.now()
    db.session.commit()
    
    return jsonify({'message': 'Checked out successfully'}), 200

@app.route('/api/attendance', methods=['GET'])
@jwt_required()
def get_attendance():
    user_id = get_jwt_identity()
    attendances = Attendance.query.filter_by(user_id=user_id).order_by(Attendance.date.desc()).all()
    
    result = []
    for attendance in attendances:
        result.append({
            'id': attendance.id,
            'date': attendance.date.isoformat(),
            'check_in': attendance.check_in.isoformat() if attendance.check_in else None,
            'check_out': attendance.check_out.isoformat() if attendance.check_out else None
        })
    
    return jsonify(result), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)