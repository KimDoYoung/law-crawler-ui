# law-crawler-ui

## 개요

- law-crawler가 수집한 데이터를 웹페이지를 보여 준다.
- 원래 streamlit으로 작성하였으나 2025-10-21 사용자 요청(웹페이지인데 보기흉하고 사용하기 불편)에 의해서 fastapi로 추가해서 개발
- streamlit소스를 그대로 두고 fastapi를 app폴더 하위에 작성하기로 함.

## 기술스택

### 특징

- 인증 기능 없음. 누구나 자유롭게 사용(실제 사용자 제한적임)

### backend

    1. fastapi
    2. sqlitedb
    3. jinja2

### frontend

    1. tailwindcss
    2. alpine

## streamlit 실행

- run_ui.bat(window), run_ui.sh(git-baash, linux)를 실행
- 환경변수 LAW_CRAWLER_EXE_DIR 가 설정되어 있어야한다.
- 환경변수 LAW_CRAWLER_EXE_DIR는 law-crawler의 기본폴더를 지칭해야 한다.
  
## 메뉴들

🔍 데이터 조회 (Data Search)
📈 통계 분석 (Statistics)
📋 로그 관리 (Log Management)
⚙️ 설정 (Settings)

## 빌드

- make_exe_ui20.sh 을 사용

    dist/law-crawler-ui/
    ├── law-crawler-ui.exe       # 메인 실행 파일
    ├── .env.local                # 환경 설정 파일 (자동 복사됨)
    ├── run.bat                   # Windows 실행 스크립트 (LAW_CRAWLER_MODE=local 설정)
    ├── run.sh                    # Linux/Mac 실행 스크립트 (LAW_CRAWLER_MODE=local 설정)
    ├── README.txt                # 사용 가이드
    ├── _internal/                # 필요한 라이브러리
    └── app/                      # 템플릿과 정적 파일  
