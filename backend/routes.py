from flask import request, jsonify
from datetime import datetime, date
from database import db
from models import User, Attendance, MakeUpClass, ImportedData, BasicInfo, AttendanceDate
from qr_service import QRService
import base64

def register_routes(app):
    @app.route('/api/users', methods=['GET', 'POST'])
    def users():
        if request.method == 'POST':
            try:
                data = request.json
                
                # Validate input
                if not data.get('name') or not data.get('email'):
                    return jsonify({'error': 'Name and email are required'}), 400
                
                # Check if user already exists
                existing_user = User.query.filter_by(email=data['email']).first()
                if existing_user:
                    return jsonify({'error': 'User with this email already exists'}), 400
                
                # Create new user
                user = User(name=data['name'], email=data['email'])
                db.session.add(user)
                db.session.commit()
                
                return jsonify(user.to_dict()), 201
                
            except Exception as e:
                db.session.rollback()
                print(f"Error creating user: {e}")
                return jsonify({'error': 'Failed to create user'}), 500
        
        # GET request
        try:
            users = User.query.all()
            return jsonify([u.to_dict() for u in users])
        except Exception as e:
            print(f"Error fetching users: {e}")
            return jsonify({'error': 'Failed to fetch users'}), 500

    @app.route('/api/users/<int:user_id>', methods=['GET', 'DELETE'])
    def user(user_id):
        try:
            user = User.query.get_or_404(user_id)
            if request.method == 'DELETE':
                db.session.delete(user)
                db.session.commit()
                return '', 204
            return jsonify(user.to_dict())
        except Exception as e:
            db.session.rollback()
            print(f"Error handling user {user_id}: {e}")
            return jsonify({'error': 'Operation failed'}), 500

    @app.route('/api/generate-qr', methods=['POST'])
    def generate_qr():
        try:
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
        except Exception as e:
            print(f"Error generating QR code: {e}")
            return jsonify({'error': 'Failed to generate QR code'}), 500

    @app.route('/api/send-qr-email', methods=['POST'])
    def send_qr_email():
        try:
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
                return jsonify({'error': 'Failed to send email. Please check email configuration.'}), 500
        except ValueError as e:
            # Handle missing email configuration
            print(f"Email configuration error: {e}")
            return jsonify({'error': 'Email configuration not set. Please configure SMTP settings in environment variables.'}), 500
        except Exception as e:
            print(f"Error sending QR email: {e}")
            return jsonify({'error': f'Failed to send email: {str(e)}'}), 500

    @app.route('/api/attendance/check', methods=['POST'])
    def check_attendance():
        try:
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
        except Exception as e:
            db.session.rollback()
            print(f"Error checking attendance: {e}")
            return jsonify({'error': 'Failed to check attendance'}), 500

    @app.route('/api/attendance', methods=['GET'])
    def get_attendance():
        try:
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
        except Exception as e:
            print(f"Error fetching attendance: {e}")
            return jsonify({'error': 'Failed to fetch attendance records'}), 500

    # 新しいエンドポイント: インポートデータの保存
    @app.route('/api/import-excel', methods=['POST'])
    def import_excel():
        try:
            data = request.json
            filename = data.get('filename', 'unknown')
            basic_info = data.get('basic_info', [])
            attendance_dates = data.get('attendance_dates', [])
            
            # ImportedDataを作成
            imported_data = ImportedData(filename=filename)
            db.session.add(imported_data)
            db.session.flush()  # IDを取得するためにflush
            
            # BasicInfoを作成
            if basic_info:
                basic = BasicInfo(imported_data_id=imported_data.id)
                
                # 基本情報を解析して保存
                if len(basic_info) >= 1:
                    basic.row1_a = basic_info[0][0] if len(basic_info[0]) > 0 else ''
                    basic.row1_b = basic_info[0][1] if len(basic_info[0]) > 1 else ''
                    basic.row1_c = basic_info[0][2] if len(basic_info[0]) > 2 else ''
                    basic.row1_d = basic_info[0][3] if len(basic_info[0]) > 3 else ''
                    
                    # 氏名などの特定フィールドを抽出
                    if basic_info[0][0] == '氏名' and len(basic_info[0]) > 1:
                        basic.name = basic_info[0][1]
                    if basic_info[0][0] == '所属' and len(basic_info[0]) > 1:
                        basic.department = basic_info[0][1]
                
                if len(basic_info) >= 2:
                    basic.row2_a = basic_info[1][0] if len(basic_info[1]) > 0 else ''
                    basic.row2_b = basic_info[1][1] if len(basic_info[1]) > 1 else ''
                    basic.row2_c = basic_info[1][2] if len(basic_info[1]) > 2 else ''
                    basic.row2_d = basic_info[1][3] if len(basic_info[1]) > 3 else ''
                    
                    if basic_info[1][0] == '所属' and len(basic_info[1]) > 1:
                        basic.department = basic_info[1][1]
                    if basic_info[1][2] == '開講期間・クラス' and len(basic_info[1]) > 3:
                        basic.period_class = basic_info[1][3]
                
                if len(basic_info) >= 3:
                    basic.row3_a = basic_info[2][0] if len(basic_info[2]) > 0 else ''
                    basic.row3_b = basic_info[2][1] if len(basic_info[2]) > 1 else ''
                    basic.row3_c = basic_info[2][2] if len(basic_info[2]) > 2 else ''
                    basic.row3_d = basic_info[2][3] if len(basic_info[2]) > 3 else ''
                    
                    if basic_info[2][0] == '授業科目' and len(basic_info[2]) > 1:
                        basic.subject = basic_info[2][1]
                    if basic_info[2][2] == '授業時間' and len(basic_info[2]) > 3:
                        basic.time_slot = basic_info[2][3]
                
                db.session.add(basic)
            
            # AttendanceDateを作成
            for item in attendance_dates:
                attendance_date = AttendanceDate(
                    imported_data_id=imported_data.id,
                    row_number=item.get('row'),
                    date_text=item.get('date'),
                    attendance_mark=item.get('attendance', ''),
                    check_in_time=item.get('checkIn', ''),
                    check_out_time=item.get('checkOut', ''),
                    hours=item.get('hours', ''),
                    notes=item.get('notes', '')
                )
                db.session.add(attendance_date)
            
            db.session.commit()
            
            return jsonify({
                'message': 'データが正常に保存されました',
                'id': imported_data.id
            }), 201
            
        except Exception as e:
            db.session.rollback()
            print(f"Error importing excel data: {e}")
            return jsonify({'error': 'データの保存に失敗しました'}), 500

    # インポートデータの一覧取得
    @app.route('/api/imported-data', methods=['GET'])
    def get_imported_data():
        try:
            imported_data_list = ImportedData.query.order_by(ImportedData.import_date.desc()).all()
            return jsonify([data.to_dict() for data in imported_data_list])
        except Exception as e:
            print(f"Error fetching imported data: {e}")
            return jsonify({'error': 'インポートデータの取得に失敗しました'}), 500

    # 特定のインポートデータの詳細取得
    @app.route('/api/imported-data/<int:data_id>', methods=['GET'])
    def get_imported_data_detail(data_id):
        try:
            imported_data = ImportedData.query.get_or_404(data_id)
            return jsonify(imported_data.to_dict())
        except Exception as e:
            print(f"Error fetching imported data detail: {e}")
            return jsonify({'error': 'データの取得に失敗しました'}), 500

    # インポートデータの削除
    @app.route('/api/imported-data/<int:data_id>', methods=['DELETE'])
    def delete_imported_data(data_id):
        try:
            imported_data = ImportedData.query.get_or_404(data_id)
            db.session.delete(imported_data)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting imported data: {e}")
            return jsonify({'error': 'データの削除に失敗しました'}), 500

    @app.route('/api/health', methods=['GET'])
    def health():
        try:
            # Test database connection
            db.session.execute('SELECT 1')
            return jsonify({'status': 'healthy', 'database': 'connected'})
        except Exception as e:
            return jsonify({'status': 'unhealthy', 'error': str(e)}), 500
        

    @app.route('/api/makeup-request', methods=['POST'])
    def makeup_request():
        try:
            data = request.json
            
            # 必須項目のチェック
            required_fields = ['name', 'subject', 'original_date', 'original_period', 'new_date', 'new_period']
            if not all(field in data for field in required_fields):
                return jsonify({'error': 'すべての項目が必要です'}), 400

            new_request = MakeUpClass(
                name=data['name'],
                subject=data['subject'],
                original_date=data['original_date'],
                original_period=data['original_period'],
                new_date=data['new_date'],
                new_period=data['new_period']
            )
            db.session.add(new_request)
            db.session.commit()
            return jsonify(new_request.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            print(f"Error creating makeup request: {e}")
            return jsonify({'error': '補講申請の作成に失敗しました'}), 500
