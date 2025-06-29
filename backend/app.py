from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import bcrypt
import qrcode
import io
import base64
from datetime import datetime, date, timedelta
import os
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)  # トークンの有効期限を明示的に設定

db = SQLAlchemy(app)
jwt = JWTManager(app)

# CORS設定を更新
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "http://localhost:5173"]}})

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

    is_admin = db.Column(db.Boolean, default=False, nullable=False)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    check_in = db.Column(db.DateTime)
    check_out = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('attendances', lazy=True))
# Health check route
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

# Error handlers
@app.errorhandler(422)
def handle_unprocessable_entity(e):
    print(f"422 Error: {e}")
    print(f"Request data: {request.get_data()}")
    print(f"Request headers: {dict(request.headers)}")
    return jsonify({'error': 'Unprocessable Entity', 'details': str(e)}), 422

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'error': 'Token has expired'}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    print(f"Missing token: {error}")
    return jsonify({'error': 'Authorization token is required'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    print(f"Invalid token: {error}")
    return jsonify({'error': 'Invalid token'}), 401

# Auth Routes
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
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
    except Exception as e:
        print(f"Registration error: {e}")
        db.session.rollback()  # ロールバックを追加
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # user.idを文字列に変換して渡す
            access_token = create_access_token(identity=str(user.id))
            return jsonify({
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_admin': user.is_admin  # 管理者情報を追加
                }
            }), 200
        
        return jsonify({'error': 'Invalid username or password'}), 401
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))  # 文字列をintに変換
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin  # 管理者情報を追加
        }), 200
    except Exception as e:
        print(f"Profile error: {e}")
        return jsonify({'error': 'Failed to get profile'}), 500

# QR Code Generation
@app.route('/api/generate-qr', methods=['POST'])
@jwt_required()
def generate_qr():
    try:
        user_id = get_jwt_identity()
        print(f"User ID from token: {user_id}")
        
        user = User.query.get(int(user_id))  # 文字列をintに変換
        
        if not user:
            print(f"User not found for ID: {user_id}")
            return jsonify({'error': 'User not found'}), 404
        
        # JSONデータを取得、なければ空のdictを使用
        data = request.get_json() or {}
        target_date = data.get('date', str(date.today()))
        
        print(f"Generating QR for user {user.username}, date: {target_date}")
        
        # QRコードに含める元のデータを作成
        original_data = f"{user.username}:{target_date}"

        # 元のデータをSHA-256でハッシュ化する
        hash_object = hashlib.sha256()
        hash_object.update(original_data.encode('utf-8'))
        hashed_data = hash_object.hexdigest()

        # QR Code data: Hashed value
        qr_data = hashed_data

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
    except Exception as e:
        print(f"QR generation error: {e}")
        return jsonify({'error': 'QR generation failed', 'details': str(e)}), 500

# Test QR endpoint
@app.route('/api/test-qr', methods=['GET'])
def test_qr():
    try:
        qr_data = "test:2024-01-01"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        img_base64 = base64.b64encode(img_io.getvalue()).decode()
        
        return jsonify({
            'qr_code': f"data:image/png;base64,{img_base64}",
            'status': 'success'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Attendance Routes
@app.route('/api/check-in', methods=['POST'])
@jwt_required()
def check_in():
    try:
        user_id = int(get_jwt_identity())  # 文字列をintに変換
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
    except Exception as e:
        print(f"Check-in error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Check-in failed'}), 500

@app.route('/api/check-out', methods=['POST'])
@jwt_required()
def check_out():
    try:
        user_id = int(get_jwt_identity())  # 文字列をintに変換
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
    except Exception as e:
        print(f"Check-out error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Check-out failed'}), 500

@app.route('/api/attendance', methods=['GET'])
@jwt_required()
def get_attendance():
    try:
        user_id = int(get_jwt_identity())  # 文字列をintに変換
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
    except Exception as e:
        print(f"Get attendance error: {e}")
        return jsonify({'error': 'Failed to get attendance'}), 500
    





# 以降管理者限定
@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
def get_all_users():
    try:
        user_id = int(get_jwt_identity())
        current_user = User.query.get(user_id)
        
        if not current_user or not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        users = User.query.all()
        result = []
        for user in users:
            result.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin,
                'created_at': user.created_at.isoformat()
            })
        
        return jsonify(result), 200
    except Exception as e:
        print(f"Get all users error: {e}")
        return jsonify({'error': 'Failed to get users'}), 500

# 全ユーザーの勤怠履歴取得（管理者のみ）
@app.route('/api/admin/attendance', methods=['GET'])
@jwt_required()
def get_all_attendance():
    try:
        user_id = int(get_jwt_identity())
        current_user = User.query.get(user_id)
        
        if not current_user or not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        # URLパラメータからuser_idを取得（オプション）
        target_user_id = request.args.get('user_id', type=int)
        
        if target_user_id:
            attendances = Attendance.query.filter_by(user_id=target_user_id).order_by(Attendance.date.desc()).all()
        else:
            attendances = Attendance.query.join(User).order_by(Attendance.date.desc()).all()
        
        result = []
        for attendance in attendances:
            result.append({
                'id': attendance.id,
                'user_id': attendance.user_id,
                'username': attendance.user.username,
                'date': attendance.date.isoformat(),
                'check_in': attendance.check_in.isoformat() if attendance.check_in else None,
                'check_out': attendance.check_out.isoformat() if attendance.check_out else None,
                'is_present': attendance.is_present,
                'class_count': attendance.class_count
            })
        
        return jsonify(result), 200
    except Exception as e:
        print(f"Get all attendance error: {e}")
        return jsonify({'error': 'Failed to get attendance'}), 500

# 管理者が勤怠記録を追加/編集（管理者のみ）
@app.route('/api/admin/attendance', methods=['POST'])
@jwt_required()
def admin_add_attendance():
    try:
        user_id = int(get_jwt_identity())
        current_user = User.query.get(user_id)
        
        if not current_user or not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        target_user_id = data.get('user_id')
        attendance_date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
        check_in_str = data.get('check_in')
        check_out_str = data.get('check_out')
        is_present = data.get('is_present', True)
        class_count = data.get('class_count', 0)
        
        if not target_user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        # 既存の記録があるかチェック
        existing_attendance = Attendance.query.filter_by(
            user_id=target_user_id,
            date=attendance_date
        ).first()
        
        check_in = None
        check_out = None
        
        if check_in_str:
            check_in = datetime.fromisoformat(check_in_str.replace('Z', '+00:00'))
        if check_out_str:
            check_out = datetime.fromisoformat(check_out_str.replace('Z', '+00:00'))
        
        if existing_attendance:
            # 既存の記録を更新
            existing_attendance.check_in = check_in
            existing_attendance.check_out = check_out
            existing_attendance.is_present = is_present
            existing_attendance.class_count = class_count
        else:
            # 新しい記録を作成
            attendance = Attendance(
                user_id=target_user_id,
                date=attendance_date,
                check_in=check_in,
                check_out=check_out,
                is_present=is_present,
                class_count=class_count
            )
            db.session.add(attendance)
        
        db.session.commit()
        return jsonify({'message': 'Attendance record saved successfully'}), 200
    except Exception as e:
        print(f"Admin add attendance error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to save attendance record'}), 500

# 管理者が勤怠記録を削除（管理者のみ）
@app.route('/api/admin/attendance/<int:attendance_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_attendance(attendance_id):
    try:
        user_id = int(get_jwt_identity())
        current_user = User.query.get(user_id)
        
        if not current_user or not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        attendance = Attendance.query.get(attendance_id)
        if not attendance:
            return jsonify({'error': 'Attendance record not found'}), 404
        
        db.session.delete(attendance)
        db.session.commit()
        
        return jsonify({'message': 'Attendance record deleted successfully'}), 200
    except Exception as e:
        print(f"Admin delete attendance error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete attendance record'}), 500








if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created successfully")
        
        # 管理者アカウントが存在しない場合は作成
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin_user.set_password('admin')  # パスワードを'admin'に修正
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created: username=admin, password=admin")
        else:
            print("Admin user already exists")
            
    app.run(host='0.0.0.0', port=5000, debug=True)