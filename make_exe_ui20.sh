#!/bin/bash

# Law Crawler UI - PyInstaller 빌드 스크립트
# PyInstaller를 사용하여 실행 파일을 생성합니다.

echo "=========================================="
echo "Law Crawler UI - 빌드 시작"
echo "=========================================="

# 현재 디렉토리 확인
echo "📁 현재 디렉토리: $(pwd)"

# 1. PyInstaller 설치 확인 및 설치
echo ""
echo "📦 PyInstaller 설치 확인..."
if ! command -v pyinstaller &> /dev/null; then
    echo "⚠️  PyInstaller가 설치되어 있지 않습니다."
    echo "🔧 PyInstaller 설치 중..."
    uv pip install pyinstaller
    if [ $? -ne 0 ]; then
        echo "❌ PyInstaller 설치 실패"
        exit 1
    fi
else
    echo "✅ PyInstaller가 이미 설치되어 있습니다."
fi

# 2. 이전 빌드 결과 삭제
echo ""
echo "🗑️  이전 빌드 결과 삭제 중..."
if [ -d "dist" ]; then
    rm -rf dist
    echo "   ✓ dist 폴더 삭제 완료"
fi
if [ -d "build" ]; then
    rm -rf build
    echo "   ✓ build 폴더 삭제 완료"
fi

# 3. PyInstaller로 빌드
echo ""
echo "🔨 PyInstaller 빌드 시작..."
echo "   - 빌드 모드: 폴더 (onedir)"
echo "   - 시작 파일: app/backend/main.py"
echo "   - 출력 디렉토리: dist/law-crawler-ui/"
echo ""

pyinstaller law_crawler_ui_ui20.spec

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 빌드 실패!"
    exit 1
fi

# 4. 빌드 결과 확인
echo ""
echo "=========================================="
echo "✅ 빌드 완료!"
echo "=========================================="
echo ""
echo "📂 빌드 결과 위치:"
echo "   $(pwd)/dist/law-crawler-ui/"
echo ""
echo "🚀 실행 방법:"
echo "   cd dist/law-crawler-ui"
echo "   ./run.sh"
echo ""
echo "📋 참고사항:"
echo "   - dist/law-crawler-ui 폴더 전체를 배포해야 합니다"
echo "   - .env.local 파일에서 CRAWLER_BASE_DIR 경로를 수정하세요"
echo ""
echo "=========================================="

# 5. .env.local 파일 복사
echo ""
echo "📋 환경 설정 파일 복사 중..."
if [ -f ".env.local" ]; then
    cp .env.local dist/law-crawler-ui/.env.local
    echo "   ✓ .env.local 파일 복사 완료"
else
    echo "   ⚠️  .env.local 파일이 없습니다. 수동으로 생성하세요."
fi

# 6. dist 폴더에 run.bat 생성
echo ""
echo "📝 실행 스크립트 생성 중..."
cat > dist/law-crawler-ui/run.bat << 'EOF'
@echo off
chcp 65001 >nul

REM 포트 설정 (인자로 받거나 기본값 8000)
set PORT=%1
if "%PORT%"=="" set PORT=8000

set LAW_CRAWLER_MODE=local

echo ==========================================
echo Law Crawler UI Start
echo ==========================================
echo.
echo LAW_CRAWLER_MODE: %LAW_CRAWLER_MODE%
echo Server Port: %PORT%
echo Server starting...
echo Open browser: http://localhost:%PORT%
echo.
echo Press Ctrl+C to stop
echo ==========================================
echo.

%~dp0law-crawler-ui.exe --host 0.0.0.0 --port %PORT%

pause
EOF
echo "   ✓ run.bat 생성 완료"

# 7. dist 폴더에 run.sh 생성
cat > dist/law-crawler-ui/run.sh << 'EOF'
#!/bin/bash

# Law Crawler UI - 실행 스크립트

# 포트 설정 (인자로 받거나 기본값 8000)
PORT=${1:-8000}

# LAW_CRAWLER_MODE 환경 변수 설정
export LAW_CRAWLER_MODE=local

echo "=========================================="
echo "Law Crawler UI Start"
echo "=========================================="
echo ""
echo "LAW_CRAWLER_MODE: $LAW_CRAWLER_MODE"
echo "Server Port: $PORT"
echo "Server starting..."
echo "Open browser: http://localhost:$PORT"
echo ""
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

./law-crawler-ui --host 0.0.0.0 --port $PORT
EOF
chmod +x dist/law-crawler-ui/run.sh
echo "   ✓ run.sh 생성 완료"

# 8. 배포 폴더에 README 추가
echo ""
cat > dist/law-crawler-ui/README.txt << 'EOF'
===========================================
Law Crawler UI - 실행 가이드
===========================================

1. 환경 설정
   - .env.local 파일에서 경로를 수정하세요
   - CRAWLER_BASE_DIR=/path/to/law-crawler

2. 실행 방법
   Windows:
     run.bat           (기본 포트 8000)
     run.bat 9000      (포트 9000으로 실행)

   Linux/Mac:
     chmod +x run.sh
     ./run.sh          (기본 포트 8000)
     ./run.sh 9000     (포트 9000으로 실행)

3. 접속
   브라우저에서 http://localhost:8000 접속
   (포트를 변경한 경우 해당 포트로 접속)

4. 종료
   Ctrl+C 또는 터미널 종료

===========================================
EOF
echo "📄 README.txt 파일 생성 완료"
echo ""

echo "=========================================="
echo "📦 배포 파일 목록:"
echo "   - law-crawler-ui         (메인 실행 파일)"
echo "   - .env.local             (환경 설정)"
echo "   - run.bat                (Windows 실행 스크립트)"
echo "   - run.sh                 (Linux/Mac 실행 스크립트)"
echo "   - README.txt             (사용 가이드)"
echo "   - _internal/             (필요한 라이브러리)"
echo "=========================================="
echo ""

# 9. c:/law-crawler-ui로 복사
echo "📋 c:/law-crawler-ui 폴더로 배포 파일 복사 중..."
if [ ! -d "c:/law-crawler-ui" ]; then
    mkdir -p "c:/law-crawler-ui"
    echo "   ✓ c:/law-crawler-ui 폴더 생성 완료"
else
    rm -rf c:/law-crawler-ui/*
    echo "   ✓ c:/law-crawler-ui 폴더 내용 삭제 완료"
fi
cp -r ./dist/law-crawler-ui/* c:/law-crawler-ui/
echo "   ✓ 배포 파일 복사 완료"
echo ""

echo "=========================================="
echo "✅ 빌드 결과가 c:/law-crawler-ui/ 로 복사되었습니다"
echo "=========================================="
echo ""
echo "🚀 실행 방법:"
echo "   cd c:/law-crawler-ui"
echo "   run.bat         (Windows, 기본 포트 8000)"
echo "   run.bat 9000    (Windows, 포트 9000)"
echo "   ./run.sh        (Linux/Mac, 기본 포트 8000)"
echo "   ./run.sh 9000   (Linux/Mac, 포트 9000)"
echo ""
