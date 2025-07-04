from flask import request, jsonify
from datetime import datetime, date
from database import db
from models import User, Attendance
from qr_service import QRService
import base64

def register_routes(app):
    @app.route('/api/users', methods=['GET', 'POST'])
    def users():
        if request.method == 'POST':
            data = request.json
            
            # Check if user already exists
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                return jsonify({'error': 'User with this email already exists'}), 400
            
            user = User(name=data['name'], email=data['email'])
            db.session.add(user)
            db.session.commit()
            return jsonify(user.to_dict()), 201
        
        users = User.query.all()
        return jsonify([u.to_dict() for u in users])

    @app.route('/api/users/<int:user_id>', methods=['GET', 'DELETE'])
    def user(user_id):
        user = User.query.get_or_404(user_id)
        if request.method == 'DELETE':
            db.session.delete(user)
            db.session.commit()
            return '', 204
        return jsonify(user.to_dict())

    @app.route('/api/generate-qr', methods=['POST'])
    def generate_qr():
        data = request.json
        user_id = data.get('user_id')
        target_date = data.get('date', date.today().isoformat())
        
        user = User.query.get_or_404(user_id)
        
        # Generate QR code
        qr_image_io, qr_data = QRService.generate_qr_code(user.name, target_date)
        
        # Convert to base64 for response
        qr_image_io.seek(0)
        qr_base64 = base64.b64encode(qr_image_io.read()).decode('utf-8')
        
        return jsonify({
            'qr_code': f'data:image/png;base64,{qr_base64}',
            'qr_data': qr_data
        })

    @app.route('/api/send-qr-email', methods=['POST'])
    def send_qr_email():
        data = request.json
        user_id = data.get('user_id')
        target_date = data.get('date', date.today().isoformat())
        
        user = User.query.get_or_404(user_id)
        
        # Generate QR code
        qr_image_io, qr_data = QRService.generate_qr_code(user.name, target_date)
        
        # Send email
        success = QRService.send_qr_email(user.email, user.name, qr_image_io, target_date)
        
        if success:
            return jsonify({'message': 'QR code sent successfully', 'qr_data': qr_data})
        else:
            return jsonify({'error': 'Failed to send email'}), 500

    @app.route('/api/attendance/check', methods=['POST'])
    def check_attendance():
        data = request.json
        qr_data = data.get('qr_data')
        
        if not qr_data:
            return jsonify({'error': 'QR data is required'}), 400
        
        # Parse QR data
        try:
            user_name, target_date = qr_data.split('|')
        except ValueError:
            return jsonify({'error': 'Invalid QR code format'}), 400
        
        # Find user
        user = User.query.filter_by(name=user_name).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Parse date
        try:
            target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
        
        # Check if attendance record exists for this date
        attendance = Attendance.query.filter_by(
            user_id=user.id,
            date=target_date_obj
        ).first()
        
        current_time = datetime.now()
        
        if not attendance:
            # Create new attendance record (check-in)
            attendance = Attendance(
                user_id=user.id,
                date=target_date_obj,
                check_in=current_time
            )
            db.session.add(attendance)
            db.session.commit()
            return jsonify({
                'message': 'Checked in successfully',
                'attendance': attendance.to_dict()
            })
        elif not attendance.check_out:
            # Update existing record (check-out)
            attendance.check_out = current_time
            db.session.commit()
            return jsonify({
                'message': 'Checked out successfully',
                'attendance': attendance.to_dict()
            })
        else:
            return jsonify({
                'error': 'Attendance already completed for this date',
                'attendance': attendance.to_dict()
            }), 400

    @app.route('/api/attendance', methods=['GET'])
    def get_attendance():
        user_id = request.args.get('user_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = Attendance.query
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        if start_date:
            query = query.filter(Attendance.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        
        if end_date:
            query = query.filter(Attendance.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        attendances = query.order_by(Attendance.date.desc()).all()
        
        # Include user information
        result = []
        for attendance in attendances:
            att_dict = attendance.to_dict()
            att_dict['user'] = attendance.user.to_dict()
            result.append(att_dict)
        
        return jsonify(result)

    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({'status': 'healthy'})