# 勤怠管理システム

Flask + Svelte + SQLite + SQLAlchemy を使用した勤怠管理システム

## 機能

- ユーザー管理（登録・削除）
- QRコード生成（ユーザー名と日付を含む）
- メールでQRコード送信
- QRコード読取による打刻（出勤・退勤）
- 勤怠記録の閲覧・フィルタリング

## 技術スタック

### バックエンド
- Python 3.11
- Flask 3.0.0
- SQLAlchemy
- SQLite

### フロントエンド
- Svelte 4.2.0

## セットアップ

### 1. Gmailアプリパスワードの取得

1. [Googleアカウント設定](https://myaccount.google.com/security)で2段階認証を有効化
2. [アプリパスワード](https://myaccount.google.com/apppasswords)を生成
3. 生成された16文字のパスワードをルートディレクトリの`.env`の`SMTP_PASSWORD`に設定（スペースなし）

### 2. 環境変数の設定

以下の`.env`ファイルをプロジェクトのルートディレクトリに作成
SMTP_PASSWORDは半角スペースを消す
SMTP_USERNAME,FROM_EMAILは同じメールアドレスを指定する

```
# Database
DATABASE_URL=sqlite:////data/attendance.db

# Email configuration (Gmail with App Password)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=yourapppasswordwithoutspaces
FROM_EMAIL=your-email@gmail.com
```

### 4. Dockerコンテナの起動

```bash
docker compose up -d --build
```

## 使用方法

1. ブラウザで http://localhost:3001 にアクセス
2. 「ユーザー管理」タブでユーザーを登録
3. 「QRコード生成」タブでQRコードを生成・メール送信
4. 「QRコード読取」タブでQRコードをスキャンして打刻
5. 「勤怠記録」タブで勤怠履歴を確認

## API エンドポイント

- `GET /api/users` - ユーザー一覧取得
- `POST /api/users` - ユーザー登録
- `DELETE /api/users/{id}` - ユーザー削除
- `POST /api/generate-qr` - QRコード生成
- `POST /api/send-qr-email` - QRコードメール送信
- `POST /api/attendance/check` - 打刻
- `GET /api/attendance` - 勤怠記録取得

## トラブルシューティング

### メール送信エラー
- `.env`ファイルのSMTP設定を確認
- Gmailの2段階認証とアプリパスワードを確認
- `docker logs backend`でエラーログを確認
