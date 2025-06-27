# 勤怠管理システム
Flask + Svelte + SQLite + SQLAlchemy を使用したシンプルな勤怠管理システムです。
## 機能

アカウント登録・ログイン
QRコード生成（日付とユーザー名）
出勤・退勤記録
勤怠履歴表示

## セットアップ
バックエンド (Flask)
サーバーは http://localhost:5000 で起動します。
フロントエンド (Svelte)
フロントエンドは http://localhost:3000 で起動します。

## 使用方法
docker compose up -d --build
を実行した後、
ブラウザで http://localhost:3000 にアクセス

新規登録でアカウントを作成
ログイン後、以下の機能が利用可能：

QRコード生成：日付を選択してQRコードを生成
出勤・退勤：ボタンをクリックして記録
勤怠履歴：過去の出勤・退勤記録を表示



API エンドポイント
認証

POST /api/register - ユーザー登録
POST /api/login - ログイン
GET /api/profile - ユーザー情報取得

QRコード

POST /api/generate-qr - QRコード生成

勤怠

POST /api/check-in - 出勤記録
POST /api/check-out - 退勤記録
GET /api/attendance - 勤怠履歴取得

データベース
SQLiteを使用し、以下のテーブルが自動作成されます：

users (ユーザー情報)
attendance (勤怠記録)

データベースファイルは backend/attendance.db に保存されます。
