@echo off
chcp 65001 > nul
REM Law Crawler UI - PyInstaller 빌드 스크립트 (Windows)
REM PyInstaller를 사용하여 실행 파일을 생성합니다.

echo ==========================================
echo Law Crawler UI - 빌드 시작
echo ==========================================
echo.

REM 현재 디렉토리 확인
echo 📁 현재 디렉토리: %CD%
echo.

REM 1. PyInstaller 설치 확인 및 설치
echo 📦 PyInstaller 설치 확인...
pyinstaller --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  PyInstaller가 설치되어 있지 않습니다.
    echo 🔧 PyInstaller 설치 중...
    uv pip install pyinstaller
    if %errorlevel% neq 0 (
        echo ❌ PyInstaller 설치 실패
        pause
        exit /b 1
    )
) else (
    echo ✅ PyInstaller가 이미 설치되어 있습니다.
)
echo.

REM 2. 이전 빌드 결과 삭제
echo 🗑️  이전 빌드 결과 삭제 중...
if exist "dist" (
    rmdir /s /q dist
    echo    ✓ dist 폴더 삭제 완료
)
if exist "build" (
    rmdir /s /q build
    echo    ✓ build 폴더 삭제 완료
)
echo.

REM 3. PyInstaller로 빌드
echo 🔨 PyInstaller 빌드 시작...
echo    - 빌드 모드: 폴더 (onedir)
echo    - 시작 파일: app/backend/main.py
echo    - 출력 디렉토리: dist/law-crawler-ui/
echo.

pyinstaller law_crawler_ui_ui20.spec

if %errorlevel% neq 0 (
    echo.
    echo ❌ 빌드 실패!
    pause
    exit /b 1
)

REM 4. 빌드 결과 확인
echo.
echo ==========================================
echo ✅ 빌드 완료!
echo ==========================================
echo.
echo 📂 빌드 결과 위치:
echo    %CD%\dist\law-crawler-ui\
echo.
echo 🚀 실행 방법:
echo    cd dist\law-crawler-ui
echo    run.bat
echo.
echo 📋 참고사항:
echo    - dist\law-crawler-ui 폴더 전체를 배포해야 합니다
echo    - .env.local 파일에서 CRAWLER_BASE_DIR 경로를 수정하세요
echo.
echo ==========================================

REM 5. .env.local 파일 복사
echo 📋 환경 설정 파일 복사 중...
if exist ".env.local" (
    copy /Y .env.local dist\law-crawler-ui\.env.local > nul
    echo    ✓ .env.local 파일 복사 완료
) else (
    echo    ⚠️  .env.local 파일이 없습니다. 수동으로 생성하세요.
)
echo.

REM 6. dist 폴더에 run.bat 생성
echo 📝 실행 스크립트 생성 중...
(
echo @echo off
echo chcp 65001 ^>nul
echo.
echo REM 포트 설정 (인자로 받거나 기본값 8000)
echo set PORT=%%1
echo if "%%PORT%%"=="" set PORT=8000
echo.
echo set LAW_CRAWLER_MODE=local
echo.
echo echo ==========================================
echo echo Law Crawler UI Start
echo echo ==========================================
echo echo.
echo echo LAW_CRAWLER_MODE: %%LAW_CRAWLER_MODE%%
echo echo Server Port: %%PORT%%
echo echo Server starting...
echo echo Open browser: http://localhost:%%PORT%%
echo echo.
echo echo Press Ctrl+C to stop
echo echo ==========================================
echo echo.
echo.
echo %%~dp0law-crawler-ui.exe --host 0.0.0.0 --port %%PORT%%
echo.
echo pause
) > dist\law-crawler-ui\run.bat
echo    ✓ run.bat 생성 완료
echo.

REM 7. dist 폴더에 run.sh 생성
(
echo #!/bin/bash
echo.
echo # Law Crawler UI - 실행 스크립트
echo.
echo # 포트 설정 (인자로 받거나 기본값 8000)
echo PORT=${1:-8000}
echo.
echo # LAW_CRAWLER_MODE 환경 변수 설정
echo export LAW_CRAWLER_MODE=local
echo.
echo echo "=========================================="
echo echo "Law Crawler UI Start"
echo echo "=========================================="
echo echo ""
echo echo "LAW_CRAWLER_MODE: $LAW_CRAWLER_MODE"
echo echo "Server Port: $PORT"
echo echo "Server starting..."
echo echo "Open browser: http://localhost:$PORT"
echo echo ""
echo echo "Press Ctrl+C to stop"
echo echo "=========================================="
echo echo ""
echo.
echo ./law-crawler-ui --host 0.0.0.0 --port $PORT
) > dist\law-crawler-ui\run.sh
echo    ✓ run.sh 생성 완료
echo.

REM 8. 배포 폴더에 README 추가
(
echo ===========================================
echo Law Crawler UI - 실행 가이드
echo ===========================================
echo.
echo 1. 환경 설정
echo    - .env.local 파일에서 경로를 수정하세요
echo    - CRAWLER_BASE_DIR=C:\law-crawler
echo.
echo 2. 실행 방법
echo    Windows:
echo      run.bat           (기본 포트 8000)
echo      run.bat 9000      (포트 9000으로 실행)
echo.
echo    Linux/Mac:
echo      chmod +x run.sh
echo      ./run.sh          (기본 포트 8000)
echo      ./run.sh 9000     (포트 9000으로 실행)
echo.
echo 3. 접속
echo    브라우저에서 http://localhost:8000 접속
echo    (포트를 변경한 경우 해당 포트로 접속)
echo.
echo 4. 종료
echo    Ctrl+C 또는 터미널 종료
echo.
echo ===========================================
) > dist\law-crawler-ui\README.txt
echo 📄 README.txt 파일 생성 완료
echo.

echo ==========================================
echo 📦 배포 파일 목록:
echo    - law-crawler-ui.exe  (메인 실행 파일)
echo    - .env.local          (환경 설정)
echo    - run.bat             (Windows 실행 스크립트)
echo    - run.sh              (Linux/Mac 실행 스크립트)
echo    - README.txt          (사용 가이드)
echo    - _internal/          (필요한 라이브러리)
echo ==========================================
echo.

REM 9. c:/law-crawler-ui로 복사
echo 📋 c:/law-crawler-ui 폴더로 배포 파일 복사 중...
if not exist "c:\law-crawler-ui" (
    mkdir c:\law-crawler-ui
    echo    ✓ c:/law-crawler-ui 폴더 생성 완료
) else (
    del /q c:\law-crawler-ui\*.* 2>nul
    for /d %%p in (c:\law-crawler-ui\*) do rmdir /s /q "%%p" 2>nul
    echo    ✓ c:/law-crawler-ui 폴더 내용 삭제 완료
)
xcopy /E /I /Y dist\law-crawler-ui\* c:\law-crawler-ui\ > nul
echo    ✓ 배포 파일 복사 완료
echo.

echo ==========================================
echo ✅ 빌드 결과가 c:/law-crawler-ui/ 로 복사되었습니다
echo ==========================================
echo.
echo 🚀 실행 방법:
echo    cd c:\law-crawler-ui
echo    run.bat         (Windows, 기본 포트 8000)
echo    run.bat 9000    (Windows, 포트 9000)
echo.
pause
