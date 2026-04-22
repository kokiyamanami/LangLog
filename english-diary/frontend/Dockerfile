# LangLog Frontend Dockerfile
# Node.js 18 ベースイメージ
FROM node:18-alpine

# 作業ディレクトリを設定
WORKDIR /app

# パッケージファイルをコピー
COPY frontend/package*.json ./

# 依存パッケージをインストール（@heroicons/react を含む）
RUN npm install

# ソースコード全体をコピー（src, public, index.html, vite.config.js など）
COPY frontend/ .

# Vite 開発サーバーを起動（ポート 3000 で待機、全インターフェースをリッスン）
EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
