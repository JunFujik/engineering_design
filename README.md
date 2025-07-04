# 勤怠管理システム
Flask + Svelte + SQLite + SQLAlchemy を使用した勤怠管理システム

## 機能

- メールに対して「User名+日付」を格納したQRコードを送信する
- QRコードを付属のORMで読み込んだ場合、DBに打刻する

## セットアップ
バックエンド (Flask)
サーバーは http://localhost:5000 で起動します。
フロントエンド (Svelte)
フロントエンドは http://localhost:3001 で起動します。

## 使用方法
docker compose up -d --build
を実行した後、
ブラウザで http://localhost:3001 にアクセス