:: run_ui.bat  (이모지 제거, 가상환경 지원, python -m streamlit 사용)

@echo off
REM 1) UTF-8 코드페이지(선택 사항)
chcp 65001 >nul

REM 2) 현재 배치 파일 경로로 이동
cd /d "%~dp0"

REM 3) 가상환경(.venv) 활성화 시도 ─ 없으면 건너뜀
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
    echo [INFO] .venv 활성화 완료
) else (
    echo [INFO] .venv 폴더가 없으므로 시스템 Python 사용
)

REM 4) 필수 경로·파일 점검 (ASCII만 사용)
set "LAW_CRAWLER_EXE_DIR=C:\law-crawler\exe"

if not exist "%LAW_CRAWLER_EXE_DIR%" (
    echo [ERROR] 디렉터리 %LAW_CRAWLER_EXE_DIR% 가 없습니다.
    pause & exit /b 1
)
if not exist "%LAW_CRAWLER_EXE_DIR%\.env" (
    echo [ERROR] .env 파일이 없습니다.
    pause & exit /b 1
)
if not exist "%LAW_CRAWLER_EXE_DIR%\LAW_SITE_DESC.yaml" (
    echo [ERROR] LAW_SITE_DESC.yaml 파일이 없습니다.
    pause & exit /b 1
)

REM 5) Streamlit 앱 실행
echo [INFO] Streamlit UI 실행 중...
python -m streamlit run ui\app.py %*

