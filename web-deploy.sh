#!/bin/bash

# Law Crawler UI 배포 스크립트

DEPLOY_DIR="$HOME/law-crawler/ui"

echo "🚀 Deploying Law Crawler UI..."
echo "================================"

# 배포 디렉토리 생성
if [ -d "$DEPLOY_DIR" ]; then
    echo "🧹 Cleaning up existing directory..."
    # .venv 명시적 삭제 (심볼릭 링크도 포함)
    if [ -L "$DEPLOY_DIR/.venv" ] || [ -d "$DEPLOY_DIR/.venv" ]; then
        rm -rf "$DEPLOY_DIR/.venv"
    fi
    # 다른 모든 파일 삭제
    rm -rf "${DEPLOY_DIR:?}"/*
else
    echo "📁 Creating deploy directory..."
    mkdir -p "$DEPLOY_DIR"
fi

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

# web-service.sh 복사
echo "⚙️  Copying web-service.sh..."
cp ./web-service.sh "$DEPLOY_DIR/"


echo ""
echo "✅ Deployment complete!"
echo "📂 Files deployed to: $DEPLOY_DIR"
echo ""
ls -la "$DEPLOY_DIR"
echo "================================"
echo "web-service.sh stop 명령어로 기존 서비스를 중지한 후,"
echo "uv venv && source .venv/bin/activate && web-service.sh start 명령어로 새로 배포된 UI를 시작하세요."
echo "================================"