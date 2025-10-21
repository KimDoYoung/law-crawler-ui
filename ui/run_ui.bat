@echo off
REM 환경변수 설정
set "LAW_CRAWLER_EXE_DIR=C:\law_crawler\exe"

REM 디렉토리 존재 확인
if not exist "%LAW_CRAWLER_EXE_DIR%" (
    echo ❌ 디렉토리 %LAW_CRAWLER_EXE_DIR% 가 존재하지 않습니다.
    exit /b 1
)

REM 필수 파일 확인
if not exist "%LAW_CRAWLER_EXE_DIR%\.env" (
    echo ❌ %LAW_CRAWLER_EXE_DIR%\.env 파일이 없습니다.
    exit /b 1
)

if not exist "%LAW_CRAWLER_EXE_DIR%\LAW_SITE_DESC.yaml" (
    echo ❌ %LAW_CRAWLER_EXE_DIR%\LAW_SITE_DESC.yaml 파일이 없습니다.
    exit /b 1
)

REM Streamlit 실행
@REM cd /d "%LAW_CRAWLER_EXE_DIR%"
streamlit run app.py
