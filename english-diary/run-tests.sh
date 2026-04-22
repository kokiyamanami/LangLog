#!/bin/bash
# バックエンドテスト実行スクリプト

set -e

echo "🧪 Backend tests starting..."
echo "================================"

# テストディレクトリに移動
cd backend

# pytest実行
python -m pytest tests/ \
    -v \
    --tb=short \
    --cov=app \
    --cov-report=xml \
    --cov-report=term-missing

echo "================================"
echo "✅ Tests completed successfully!"
