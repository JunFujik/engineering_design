from flask import request, jsonify, session

# パスワード設定
ADMIN_PASSWORD = "tmcit2025"
STAFF_PASSWORD = "ss"

def register_auth_routes(app):
    """認証関連のルートを登録"""

    # 管理者ログイン
    @app.route('/api/auth/login', methods=['POST'], endpoint='admin_login')
    def login():
        try:
            data = request.json
            password = data.get('password')

            if not password:
                return jsonify({'error': 'パスワードが必要です'}), 400

            if password == ADMIN_PASSWORD:
                session['logged_in'] = True
                session['staff_logged_in'] = False
                return jsonify({'message': 'ログインしました', 'logged_in': True})
            else:
                return jsonify({'error': 'パスワードが間違っています'}), 401

        except Exception as e:
            print(f"Login error: {e}")
            return jsonify({'error': 'ログインに失敗しました'}), 500

    # 連絡員ログイン
    @app.route('/api/auth/staff-login', methods=['POST'], endpoint='staff_login')
    def staff_login():
        try:
            data = request.json
            password = data.get('password')

            if not password:
                return jsonify({'error': 'パスワードが必要です'}), 400

            if password == STAFF_PASSWORD:
                session['staff_logged_in'] = True
                session['logged_in'] = False
                return jsonify({'message': '連絡員としてログインしました', 'staff_logged_in': True})
            else:
                return jsonify({'error': 'パスワードが間違っています'}), 401

        except Exception as e:
            print(f"Staff Login error: {e}")
            return jsonify({'error': 'ログインに失敗しました'}), 500

    # ログアウト
    @app.route('/api/auth/logout', methods=['POST'], endpoint='auth_logout')
    def logout():
        try:
            session.pop('logged_in', None)
            session.pop('staff_logged_in', None)
            return jsonify({'message': 'ログアウトしました', 'logged_in': False, 'staff_logged_in': False})
        except Exception as e:
            print(f"Logout error: {e}")
            return jsonify({'error': 'ログアウトに失敗しました'}), 500

    # ステータス確認
    @app.route('/api/auth/status', methods=['GET'], endpoint='auth_status')
    def auth_status():
        try:
            logged_in = session.get('logged_in', False)
            staff_logged_in = session.get('staff_logged_in', False)
            return jsonify({'logged_in': logged_in, 'staff_logged_in': staff_logged_in})
        except Exception as e:
            print(f"Auth status error: {e}")
            return jsonify({'error': 'ステータスの取得に失敗しました'}), 500
