from datetime import datetime
from database import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    attendances = db.relationship('Attendance', backref='user', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    check_in = db.Column(db.DateTime)
    check_out = db.Column(db.DateTime)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'check_in': self.check_in.isoformat() if self.check_in else None,
            'check_out': self.check_out.isoformat() if self.check_out else None,
            'date': self.date.isoformat() if self.date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# 補講関連のモデル
class MakeUpClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    original_date = db.Column(db.String(50), nullable=False)
    original_period = db.Column(db.String(50), nullable=False)
    new_date = db.Column(db.String(50), nullable=False)
    new_period = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'subject': self.subject,
            'original_date': self.original_date,
            'original_period': self.original_period,
            'new_date': self.new_date,
            'new_period': self.new_period,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# 新しいモデル: インポートしたExcelデータを保存
class ImportedData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    import_date = db.Column(db.DateTime, default=datetime.utcnow)
    basic_info = db.relationship('BasicInfo', backref='imported_data', uselist=False, cascade='all, delete-orphan')
    attendance_dates = db.relationship('AttendanceDate', backref='imported_data', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'import_date': self.import_date.isoformat() if self.import_date else None,
            'basic_info': self.basic_info.to_dict() if self.basic_info else None,
            'attendance_dates': [ad.to_dict() for ad in self.attendance_dates]
        }

class BasicInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    imported_data_id = db.Column(db.Integer, db.ForeignKey('imported_data.id'), nullable=False)
    name = db.Column(db.String(100))
    department = db.Column(db.String(100))
    subject = db.Column(db.String(100))
    schedule = db.Column(db.String(100))
    period_class = db.Column(db.String(100))
    time_slot = db.Column(db.String(100))
    # A5-D7の範囲のデータを格納
    row1_a = db.Column(db.String(100))
    row1_b = db.Column(db.String(100))
    row1_c = db.Column(db.String(100))
    row1_d = db.Column(db.String(100))
    row2_a = db.Column(db.String(100))
    row2_b = db.Column(db.String(100))
    row2_c = db.Column(db.String(100))
    row2_d = db.Column(db.String(100))
    row3_a = db.Column(db.String(100))
    row3_b = db.Column(db.String(100))
    row3_c = db.Column(db.String(100))
    row3_d = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'department': self.department,
            'subject': self.subject,
            'schedule': self.schedule,
            'period_class': self.period_class,
            'time_slot': self.time_slot,
            'range_data': [
                [self.row1_a or '', self.row1_b or '', self.row1_c or '', self.row1_d or ''],
                [self.row2_a or '', self.row2_b or '', self.row2_c or '', self.row2_d or ''],
                [self.row3_a or '', self.row3_b or '', self.row3_c or '', self.row3_d or '']
            ]
        }

class AttendanceDate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    imported_data_id = db.Column(db.Integer, db.ForeignKey('imported_data.id'), nullable=False)
    row_number = db.Column(db.Integer)
    date_text = db.Column(db.String(50))
    attendance_mark = db.Column(db.String(10))
    check_in_time = db.Column(db.String(20))
    check_out_time = db.Column(db.String(20))
    hours = db.Column(db.String(10))
    notes = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'row_number': self.row_number,
            'date_text': self.date_text,
            'attendance_mark': self.attendance_mark,
            'check_in_time': self.check_in_time,
            'check_out_time': self.check_out_time,
            'hours': self.hours,
            'notes': self.notes
        }

# 先生給料設定モデル
class TeacherSalary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_name = db.Column(db.String(100), nullable=False, unique=True)
    salary_per_class = db.Column(db.Integer, default=0)  # 1コマあたりの給料
    transportation_fee = db.Column(db.Integer, default=0)  # 交通費
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'teacher_name': self.teacher_name,
            'salary_per_class': self.salary_per_class,
            'transportation_fee': self.transportation_fee,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }