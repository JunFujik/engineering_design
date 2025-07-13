import os
import json
import requests
from datetime import datetime, timedelta

class GmailAuthService:
    """Gmail API認証管理サービス"""
    
    def __init__(self):
        self.client_id = os.getenv('GMAIL_CLIENT_ID')
        self.client_secret = os.getenv('GMAIL_CLIENT_SECRET')
        self.refresh_token = os.getenv('GMAIL_REFRESH_TOKEN')
        self.access_token = os.getenv('GMAIL_ACCESS_TOKEN')
        self.token_expiry = os.getenv('GMAIL_TOKEN_EXPIRY')
        
    def get_valid_access_token(self):
        """有効なアクセストークンを取得"""
        # アクセストークンが存在し、まだ有効期限内かチェック
        if self.access_token and self.token_expiry:
            try:
                expiry_time = datetime.fromisoformat(self.token_expiry)
                if datetime.now() < expiry_time - timedelta(minutes=5):  # 5分の余裕を持つ
                    return self.access_token
            except:
                pass
        
        # トークンをリフレッシュ
        return self.refresh_access_token()
    
    def refresh_access_token(self):
        """リフレッシュトークンを使用してアクセストークンを更新"""
        if not all([self.client_id, self.client_secret, self.refresh_token]):
            raise ValueError("Gmail API credentials not properly configured")
        
        url = 'https://oauth2.googleapis.com/token'
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            new_access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 3600)
            
            # 新しいトークンの有効期限を計算
            expiry_time = datetime.now() + timedelta(seconds=expires_in)
            
            # 環境変数を更新（実際のアプリケーションでは適切な方法で保存）
            os.environ['GMAIL_ACCESS_TOKEN'] = new_access_token
            os.environ['GMAIL_TOKEN_EXPIRY'] = expiry_time.isoformat()
            
            return new_access_token
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to refresh access token: {e}")
    
    @staticmethod
    def get_authorization_url():
        """OAuth2認証URLを生成"""
        client_id = os.getenv('GMAIL_CLIENT_ID')
        redirect_uri = os.getenv('GMAIL_REDIRECT_URI', 'http://localhost:5000/oauth2callback')
        
        if not client_id:
            raise ValueError("GMAIL_CLIENT_ID not configured")
        
        scope = 'https://www.googleapis.com/auth/gmail.send'
        
        auth_url = (
            f"https://accounts.google.com/o/oauth2/auth?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"scope={scope}&"
            f"response_type=code&"
            f"access_type=offline&"
            f"prompt=consent"
        )
        
        return auth_url
    
    @staticmethod
    def exchange_code_for_tokens(authorization_code):
        """認証コードをアクセストークンとリフレッシュトークンに交換"""
        client_id = os.getenv('GMAIL_CLIENT_ID')
        client_secret = os.getenv('GMAIL_CLIENT_SECRET')
        redirect_uri = os.getenv('GMAIL_REDIRECT_URI', 'http://localhost:5000/oauth2callback')
        
        if not all([client_id, client_secret]):
            raise ValueError("Gmail API credentials not configured")
        
        url = 'https://oauth2.googleapis.com/token'
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': authorization_code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri
        }
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            # トークンを環境変数に保存
            os.environ['GMAIL_ACCESS_TOKEN'] = token_data['access_token']
            os.environ['GMAIL_REFRESH_TOKEN'] = token_data.get('refresh_token', '')
            
            expires_in = token_data.get('expires_in', 3600)
            expiry_time = datetime.now() + timedelta(seconds=expires_in)
            os.environ['GMAIL_TOKEN_EXPIRY'] = expiry_time.isoformat()
            
            return token_data
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to exchange authorization code: {e}")