from flask import request, jsonify, session

# 管理者パスワード
ADMIN_PASSWORD = "tmcit2025"

def register_auth_routes(app):
    """認証関連のルートを登録"""
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        try:
            data = request.json
            password = data.get('password')
            
            if not password:
                return jsonify({'error': 'パスワードが必要です'}), 400
            
            if password == ADMIN_PASSWORD:
                session['logged_in'] = True
                return jsonify({'message': 'ログインしました', 'logged_in': True})
            else:
                return jsonify({'error': 'パスワードが間違っています'}), 401
                
        except Exception as e:
            print(f"Login error: {e}")
            return jsonify({'error': 'ログインに失敗しました'}), 500
    
    @app.route('/api/auth/logout', methods=['POST'])
    def logout():
        try:
            session.pop('logged_in', None)
            return jsonify({'message': 'ログアウトしました', 'logged_in': False})
        except Exception as e:
            print(f"Logout error: {e}")
            return jsonify({'error': 'ログアウトに失敗しました'}), 500
    
    @app.route('/api/auth/status', methods=['GET'])
    def auth_status():
        try:
            logged_in = session.get('logged_in', False)
            return jsonify({'logged_in': logged_in})
        except Exception as e:
            print(f"Auth status error: {e}")
            return jsonify({'error': 'ステータスの取得に失敗しました'}), 500