FROM alpine:latest

# SQLite3をインストール
RUN apk add --no-cache sqlite

# 作業ディレクトリを作成
WORKDIR /data

# コンテナ起動時のデフォルトコマンド
CMD ["sqlite3"]