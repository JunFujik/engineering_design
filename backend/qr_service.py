import qrcode
import io
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import smtplib
import os
from datetime import datetime

class QRService:
    @staticmethod
    def generate_qr_code(user_name, date):
        """Generate QR code containing user name and date"""
        # Create QR data
        qr_data = f"{user_name}|{date}"
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        return img_io, qr_data
    
    @staticmethod
    def send_qr_email(to_email, user_name, qr_image_io, date):
        """Send QR code via email"""
        # Email configuration
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME', '')
        smtp_password = os.getenv('SMTP_PASSWORD', '')
        from_email = os.getenv('FROM_EMAIL', smtp_username)
        
        if not smtp_username or not smtp_password:
            raise ValueError("Email configuration not set. Please set SMTP_USERNAME and SMTP_PASSWORD environment variables.")
        
        # Create message
        msg = MIMEMultipart()
        msg['Subject'] = f'勤怠管理QRコード - {user_name} ({date})'
        msg['From'] = from_email
        msg['To'] = to_email
        
        # Email body
        body = f"""
        {user_name}様

        {date}の勤怠管理用QRコードをお送りします。
        このQRコードをスキャンして打刻を行ってください。

        QRコードには以下の情報が含まれています：
        - ユーザー名: {user_name}
        - 日付: {date}

        よろしくお願いいたします。
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Attach QR code image
        qr_image_io.seek(0)
        img = MIMEImage(qr_image_io.read())
        img.add_header('Content-ID', '<qr_code>')
        img.add_header('Content-Disposition', 'attachment', filename=f'qr_{user_name}_{date}.png')
        msg.attach(img)
        
        # Send email
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False