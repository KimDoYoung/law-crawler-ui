#!/bin/bash

# 환경변수 설정
export LAW_CRAWLER_EXE_DIR="/c/law-crawler/exe"
export PYTHONPATH="."

# 디렉토리 존재 확인
if [ ! -d "$LAW_CRAWLER_EXE_DIR" ]; then
    echo "❌ 디렉토리 $LAW_CRAWLER_EXE_DIR 가 존재하지 않습니다."
    exit 1
fi

# 필수 파일 확인
if [ ! -f "$LAW_CRAWLER_EXE_DIR/.env" ]; then
    echo "❌ $LAW_CRAWLER_EXE_DIR/.env 파일이 없습니다."
    exit 1
fi

if [ ! -f "$LAW_CRAWLER_EXE_DIR/LAW_SITE_DESC.yaml" ]; then
    echo "❌ $LAW_CRAWLER_EXE_DIR/LAW_SITE_DESC.yaml 파일이 없습니다."
    exit 1
fi

# Streamlit 실행1
# cd "$LAW_CRAWLER_EXE_DIR"
streamlit run ui/app.py
