#!/bin/bash

# Law Crawler UI 배포 스크립트

DEPLOY_DIR="$HOME/law-crawler/ui"

echo "🚀 Deploying Law Crawler UI..."
echo "================================"

# 배포 디렉토리 생성
mkdir -p "$DEPLOY_DIR"

# app 폴더 복사
echo "📁 Copying app folder..."
cp -r ./app "$DEPLOY_DIR/"

# pyproject.toml 복사
echo "📄 Copying pyproject.toml..."
cp ./pyproject.toml "$DEPLOY_DIR/"

# uv.lock 복사
echo "🔒 Copying uv.lock..."
cp ./uv.lock "$DEPLOY_DIR/"

# .env.fedora 복사
echo "⚙️  Copying .env.fedora..."
cp ./.env.fedora "$DEPLOY_DIR/"

# .env.fedora 복사
echo "⚙️  Copying web-service.sh..."
cp ./web-service.sh "$DEPLOY_DIR/"


echo ""
echo "✅ Deployment complete!"
echo "📂 Files deployed to: $DEPLOY_DIR"
echo ""
ls -la "$DEPLOY_DIR"