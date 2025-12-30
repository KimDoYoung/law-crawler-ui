# Law-Crawler-UI 개발

**작성일**: 2025년 12월 30일  
**시스템명**: Law-Crawler-UI (법규사이트 정보 관리 시스템)  
**버전**: 0.1.0  
**상태**: 운영 중

---

## 📋 목차

1. [시스템 개요](#시스템-개요)
2. [시스템 아키텍처](#시스템-아키텍처)
3. [주요 기능](#주요-기능)
4. [기술 스택](#기술-스택)
5. [시스템 구성](#시스템-구성)
6. [데이터베이스](#데이터베이스)
7. [운영 정보](#운영-정보)
8. [모니터링 및 로깅](#모니터링-및-로깅)
9. [배포 및 빌드](#배포-및-빌드)
10. [주요 이슈 및 개선 사항](#주요-이슈-및-개선-사항)

---

## 시스템 개요

### 목적

**Law-Crawler-UI**는 법령정보시스템에서 크롤링한 법규관련 데이터를 조회, 분석, 관리하기 위한 웹 기반의 통합 관리 대시보드입니다. 사용자는 이 시스템을 통해 수집된 법규 데이터를 실시간으로 조회하고, 통계를 분석하며, 수집 상태를 모니터링할 수 있습니다.

### 개발 기간

- **초기 개발 (FastAPI 기반 웹 재개발)**
  - 시작일: **2025년 10월 21일** (Streamlit → FastAPI 마이그레이션 개시)
  - 완료일: **2025년 10월 24일**
  - **개발 기간**: 약 **4일** (2025-10-21 ~ 2025-10-24)
  - **최종 업데이트**: 2025년 12월 30일

### 시스템 특징

- **인증 기능 없음**: 내부 전용 시스템으로 설계되어 보안 제약이 있을 수 있음
- **다중 인터페이스**: Streamlit(기존) 및 FastAPI(신규) 기반의 두 가지 UI 제공
- **실시간 데이터 조회**: SQLite DB를 통한 빠른 데이터 접근
- **크롤러 연동**: law-crawler 시스템과 완전히 통합되어 데이터 동기화 제공
- **가벼운 구조**: 추가 인프라(Redis, Message Queue 등) 불필요

---

## 시스템 아키텍처

### 전체 구조도

```text
┌─────────────────────────────────────────────────────┐
│               클라이언트 (웹 브라우저)                │
└────────────────────┬────────────────────────────────┘
                     │ HTTP(S)
        ┌────────────┴─────────────┐
        │                          │
    ┌───▼────────────┐    ┌────────▼────────┐
    │  Streamlit UI   │    │  FastAPI App    │
    │ (ui/app.py)     │    │ (app/backend)   │
    └───┬────────────┘    └────────┬────────┘
        │                          │
        └────────────┬─────────────┘
                     │
        ┌────────────▼──────────────┐
        │   Core Components         │
        │ ├─ Config Manager         │
        │ ├─ Logger                 │
        │ ├─ Exception Handler      │
        │ ├─ Template Engine (Jinja)│
        └────────────┬──────────────┘
                     │
        ┌────────────▼──────────────┐
        │   Data Layer              │
        │ ├─ db_util.py             │
        │ ├─ log_util.py            │
        │ └─ SQLite Adapter         │
        └────────────┬──────────────┘
                     │
        ┌────────────▼──────────────┐
        │   External Resources      │
        │ ├─ law_summary.db         │
        │ ├─ Crawler Logs           │
        │ ├─ UI Logs                │
        │ └─ Attachments            │
        └───────────────────────────┘
```

### 계층 구조

| 계층 | 설명 | 주요 컴포넌트 |
|------|------|--------------|
| **Presentation** | 사용자 인터페이스 | FastAPI 라우터, HTML/CSS/JS, Tailwind CSS, Alpine.js |
| **Application** | 비즈니스 로직 | page_contexts (Dashboard, Search, Statistics, Logs, Settings) |
| **Data Access** | 데이터 접근 | db_util, log_util, SQLite 드라이버 |
| **Infrastructure** | 기반 시설 | Config, Logger, Exception Handler, Template Engine |

---

## 주요 기능

### 1. 📊 대시보드 (Dashboard)

**목적**: 법규 데이터 수집 현황을 한눈에 파악

**핵심 지표 (KPI)**:

- **수집 사이트**: 모니터링 중인 사이트 수 및 페이지 수
- **오늘 수집**: 당일 수집한 게시물 및 첨부파일 수
- **누적 통계**: 전체 기간 수집 통계
- **오류 발생**: 최근 24시간 오류 발생 현황

**데이터 표시**:

- KPI 카드 형식 (천단위 콤마 처리)
- 기간별 필터 (오늘, 3일, 7일, 전체)
- 수집 데이터 그리드 조회
- 상세 정보 탭 (렌더링 보기, HTML 코드, 첨부파일)

**구현 위치**: `app/backend/page_contexts/dashboard_context.py`

---

### 2. 🔍 데이터 조회 (Search)

**목적**: 수집된 법규 데이터의 고급 검색

**검색 옵션**:

- 다중 사이트 선택 검색
- 키워드 검색 (제목 및 요약)
- 자동 완성 및 필터링

**검색 결과**:

- 페이징 처리된 그리드 표시
- 사이트명, 페이지명, 제목, URL 정보
- 상세 정보 표시 (HTML 렌더링, 코드 뷰, 첨부파일 다운로드)

**구현 위치**: `app/backend/page_contexts/search_context.py`

---

### 3. 📈 통계 분석 (Statistics)

**탭 1: 수집 통계**

- 사이트별 게시글 수 막대 그래프
- 통계 테이블 (사이트명, 게시글수, 첨부파일수)

**탭 2: 상세 통계**

- 상세한 통계 데이터 분석

**데이터 포맷**:

- 천단위 콤마 처리
- 우측 정렬

**구현 위치**: `app/backend/page_contexts/statistics_context.py`

---

### 4. 📋 로그 관리 (Log Management)

**기능**:

- UI(웹페이지) 로그 조회
- Crawler 로그 조회
- 로그 파일 다운로드
- 날짜별 로그 필터링

**로그 구조**:

```
UI 로그: ${UI_BASE_DIR}/logs/law_crawler.log
Crawler 로그: ${CRAWLER_BASE_DIR}/logs/*.log
```

**구현 위치**: `app/backend/page_contexts/logs_context.py`

---

### 5. ⚙️ 설정 (Settings)

**기능**:

- 시스템 정보 조회
- 수집 사이트 목록 및 상태
- info.md, history.md 등 문서 조회
- 시스템 설정 정보 표시

**구현 위치**: `app/backend/page_contexts/settings_context.py`

---

## 기술 스택

### 전체 기술 스택 요약

```
Backend Framework      : FastAPI (Python 기반 비동기 웹 프레임워크)
서버                  : Uvicorn (ASGI 서버)
템플릿 엔진           : Jinja2 (HTML 동적 렌더링)
데이터베이스          : SQLite3 (경량 관계형 DB)
API 데이터 형식       : JSON (RESTful API)
프론트엔드            : HTML5 + CSS3 + JavaScript
스타일링              : Tailwind CSS (유틸리티 기반 CSS)
인터랙티비티          : Alpine.js (경량 JavaScript 프레임워크)
통신                  : Fetch API (비동기 HTTP)
배포                  : PyInstaller (Python → 실행 파일)
테스팅                : pytest (단위 테스트)
환경관리              : python-dotenv (.env 파일 관리)
```

### Backend (Python 기반)

| 기술 | 버전 | 용도 | 선택 이유 |
|------|------|------|----------|
| **Python** | >= 3.11 | 프로그래밍 언어 | 빠른 개발, 풍부한 라이브러리 |
| **FastAPI** | >= 0.119.1 | 웹 프레임워크 | 고성능, 자동 API 문서화, 타입 힌팅 |
| **Uvicorn** | >= 0.38.0 | ASGI 서버 | 비동기 처리, 높은 동시성 |
| **Jinja2** | >= 3.1.6 | 템플릿 엔진 | Django 호환, 강력한 템플릿 기능 |
| **SQLite3** | (내장) | 데이터베이스 | 파일 기반, 추가 설치 불필요, 빠른 조회 |
| **pandas** | >= 2.3.0 | 데이터 분석 | 데이터프레임 처리, 강력한 CSV/DB 지원 |
| **PyYAML** | >= 6.0.2 | 설정 파싱 | YAML 형식의 사이트 설정 파일 읽기 |
| **aiofiles** | >= 25.1.0 | 비동기 파일 I/O | 논블로킹 파일 작업 |
| **python-dotenv** | >= 1.1.0 | 환경변수 관리 | .env 파일에서 설정 로드 |
| **psutil** | >= 7.0.0 | 시스템 정보 | CPU, 메모리 등 시스템 모니터링 |
| **concurrent-log-handler** | >= 0.9.28 | 로깅 | 동시 파일 접근 처리 |

### Frontend (클라이언트)

| 기술 | 목적 | 특징 |
|------|------|------|
| **HTML5** | 마크업 | 시맨틱 마크업 사용 |
| **CSS3** | 기본 스타일 | 커스텀 스타일, 반응형 디자인 |
| **Tailwind CSS** | 유틸리티 CSS | 빠른 UI 개발, 일관된 디자인 |
| **JavaScript** | 클라이언트 로직 | 동적 상호작용 |
| **Alpine.js** | 경량 프레임워크 | jQuery 없이 DOM 조작, 상태 관리 |
| **Fetch API** | HTTP 통신 | 비동기 API 호출 |

### 개발 및 배포 도구

| 도구 | 버전 | 용도 |
|------|------|------|
| **PyInstaller** | >= 6.16.0 | Python → EXE 변환 |
| **pytest** | (지정 안함) | 단위 테스트 프레임워크 |
| **debugpy** | >= 1.8.17 | Python 디버깅 |
| **numpy** | >= 2.3.0 | 수치 계산 (pandas 의존성) |
| **streamlit** | >= 1.45.1 | Streamlit UI (레거시) |
| **streamlit-aggrid** | >= 1.1.5 | Streamlit 그리드 컴포넌트 |

### 아키텍처 패턴

```
계층        | 기술                              | 역할
-----------|-------------------------------------|--------
Presentation | FastAPI + Jinja2 + HTML/CSS/JS   | API 엔드포인트, 화면 렌더링
Business   | page_contexts (대시보드, 검색 등)  | 비즈니스 로직, 데이터 처리
Data       | db_util, log_util (pandas)        | 데이터 조회, 변환
Infra      | config, logger, exception_handler | 설정, 로깅, 예외 처리
```

---

## 시스템 구성

### 디렉터리 구조

```
law-crawler-ui/
├── app/                              # FastAPI 애플리케이션
│   ├── backend/
│   │   ├── main.py                  # 애플리케이션 진입점
│   │   ├── core/                    # 핵심 구성 요소
│   │   │   ├── config.py            # 설정 관리
│   │   │   ├── logger.py            # 로깅 설정
│   │   │   ├── exception_handler.py # 예외 처리
│   │   │   ├── exceptions.py        # 커스텀 예외
│   │   │   └── template_engine.py   # Jinja2 설정
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   └── home_routes.py   # 홈 페이지 라우터
│   │   │   └── v1/
│   │   │       ├── dashboard.py     # 대시보드 API
│   │   │       ├── search.py        # 검색 API
│   │   │       ├── statistics.py    # 통계 API
│   │   │       ├── logs.py          # 로그 API
│   │   │       ├── settings.py      # 설정 API
│   │   │       └── attachments.py   # 첨부파일 API
│   │   ├── page_contexts/           # 비즈니스 로직 (데이터 처리)
│   │   │   ├── dashboard_context.py
│   │   │   ├── search_context.py
│   │   │   ├── statistics_context.py
│   │   │   ├── logs_context.py
│   │   │   ├── settings_context.py
│   │   │   └── context_registry.py  # 컨텍스트 통합 관리
│   │   └── data/                    # 데이터 접근 계층
│   │       ├── db_util.py           # SQLite 유틸리티
│   │       └── log_util.py          # 로그 유틸리티
│   └── frontend/
│       ├── public/
│       │   ├── css/
│       │   │   └── style.css        # 커스텀 스타일
│       │   ├── js/
│       │   │   ├── common.js        # 공통 JS 유틸
│       │   │   └── fetch-util.js    # API 호출 래퍼
│       │   └── images/              # 정적 이미지
│       └── views/
│           ├── error.html           # 에러 페이지
│           ├── common/              # 공통 컴포넌트
│           │   ├── base.html        # 기본 템플릿
│           │   ├── nav.html         # 네비게이션
│           │   ├── nav_right.html   # 우측 네비게이션
│           │   ├── alert.html       # 알림
│           │   ├── error_toast.html
│           │   └── loading.html     # 로딩 표시
│           ├── template/            # 페이지 템플릿
│           │   ├── dashboard.html
│           │   ├── search.html
│           │   ├── statistics.html
│           │   ├── logs.html
│           │   └── settings.html
│           └── templates/ (deprecated)
├── ui/                              # Streamlit 애플리케이션 (레거시)
│   ├── app.py
│   ├── utils/
│   │   ├── db_manager.py
│   │   ├── db_util.py
│   │   ├── logger.py
│   │   ├── sys_util.py
│   │   ├── ui_settings.py
│   │   └── misc_utils.py
│   ├── data/                        # 로컬 데이터
│   ├── logs/                        # 로그 저장소
│   └── run_ui.bat
├── tests/                           # 테스트 코드
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_dashboard_context.py
│   ├── test_logs_context.py
│   ├── test_search_context.py
│   ├── test_settings_context.py
│   └── test_statistics_context.py
├── docs/                            # 문서
│   ├── prompt.md                    # 개발 요구사항
│   ├── table_ddl.md                 # 데이터베이스 스키마
│   └── 기능(Ver1.0).md               # 기능 설명서
├── pyproject.toml                   # 프로젝트 설정 및 의존성
├── pytest.ini                       # pytest 설정
├── README.md                        # 프로젝트 개요
├── CLAUDE.md                        # 개발자 가이드
├── run_ui.bat / run_ui.sh          # 실행 스크립트
├── make_exe_ui20.bat / .sh         # 빌드 스크립트
└── env.sample                       # 환경 변수 샘플

```

### 환경 변수

| 변수명 | 필수 | 설명 | 예시 |
|--------|------|------|------|
| `LAW_CRAWLER_MODE` | 아니오 | 프로필 모드 (local/prod) | local |
| `CRAWLER_BASE_DIR` | **예** | law-crawler 기본 디렉터리 | `C:\law-crawler` |
| `CRAWLER_LOG_DIR` | 아니오 | 크롤러 로그 디렉터리 | `${CRAWLER_BASE_DIR}/logs` |
| `CRAWLER_EXE_DIR` | 아니오 | 크롤러 실행 파일 디렉터리 | `${CRAWLER_BASE_DIR}/exe` |
| `CRAWLER_DATA_DIR` | 아니오 | 크롤러 데이터 디렉터리 | `${CRAWLER_BASE_DIR}/data` |
| `UI_BASE_DIR` | 아니오 | UI 기본 디렉터리 | `C:\law-crawler-ui` |
| `UI_LOG_DIR` | 아니오 | UI 로그 디렉터리 | `${UI_BASE_DIR}/logs` |
| `UI_LOG_LEVEL` | 아니오 | 로그 레벨 | DEBUG, INFO, WARNING, ERROR |
| `VERSION` | 아니오 | 애플리케이션 버전 | 0.1.0 |

**⚠️ 중요**: `CRAWLER_BASE_DIR` 환경 변수가 설정되지 않으면 애플리케이션 시작 시 에러 발생

---

## 데이터베이스

### 데이터베이스 개요

**위치**: `${CRAWLER_DATA_DIR}/DB/law_summary.db`  
**유형**: SQLite3  
**용도**: 법규 데이터 저장소  
**관리**: law-crawler에서 관리 (law-crawler-ui는 읽기 전용)

### 테이블 스키마

#### 1. law_summary (법규 데이터 메인 테이블)

```sql
CREATE TABLE law_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL DEFAULT 'DATA',
    site_name TEXT NOT NULL,
    page_id TEXT NOT NULL,
    real_seq TEXT,
    title TEXT,
    register_date TEXT,
    org_url TEXT,
    summary TEXT,
    upd_time DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**용도**: 법규사이트의 게시판에서 크롤링한 콘텐츠 저장

**주요 컬럼**:

- `id`: 고유 식별자
- `site_name`: 사이트명 (예: 국무조정실, 산업통상자원부)
- `page_id`: 사이트 내 페이지 식별자
- `title`: 게시물 제목
- `summary`: 게시물 요약/내용
- `register_date`: 원본 등록일
- `org_url`: 원본 URL
- `upd_time`: 수집 일시

**예상 행 수**: 수십만 건 (수집 기간에 따라 증가)

---

#### 2. law_summary_attach (첨부파일 메타데이터)

```sql
CREATE TABLE law_summary_attach (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER NOT NULL,
    save_folder TEXT,
    save_file_name TEXT,
    upd_time DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**용도**: 법규 데이터에 첨부된 파일 정보 저장

**주요 컬럼**:

- `id`: 고유 식별자
- `parent_id`: law_summary.id (외래키)
- `save_folder`: 저장 폴더 경로 (실제 파일 시스템)
- `save_file_name`: 저장된 파일명
- `upd_time`: 저장 일시

**참고**: 실제 첨부파일은 `${CRAWLER_DATA_DIR}/Attaches/` 디렉터리에 저장됨

---

#### 3. yaml_info (크롤링 대상 사이트 정보)

```sql
CREATE TABLE yaml_info (
    site_name TEXT NOT NULL,
    page_id TEXT NOT NULL,
    h_name TEXT,
    desc TEXT,
    url TEXT,
    detail_url TEXT,
    PRIMARY KEY (site_name, page_id)
);
```

**용도**: LAW_SITE_DESC.yaml에서 로드된 크롤링 대상 사이트 정보

**주요 컬럼**:

- `site_name`: 사이트명
- `page_id`: 페이지 ID
- `h_name`: 한글명
- `desc`: 설명
- `url`: 목록 조회 URL
- `detail_url`: 상세 조회 URL 패턴

**행 수**: 고정적 (크롤링 대상 사이트/페이지 수)

---

### 데이터 접근 패턴

**읽기 작업** (db_util.py):

- `get_data_frame_summary()`: SQL 쿼리 실행 및 DataFrame 반환
- `get_summary_list()`: 기간별 데이터 조회
- `site_static()`: 사이트별 통계
- `search_law_summary()`: 키워드 검색
- `attach_list()`: 첨부파일 목록

**스키마 초기화**:

- `create_and_fill_yaml_table()`: yaml_info 테이블 생성 및 초기화

---

## 운영 정보

### 실행 방식

#### FastAPI 애플리케이션 (권장)

```bash
# Windows
python app/backend/main.py

# 또는 직접 Uvicorn 실행
uvicorn app.backend.main:create_app --host 0.0.0.0 --port 8000
```

**접근 URL**: `http://localhost:8000`

**커스텀 옵션**:

```bash
python app/backend/main.py --host 0.0.0.0 --port 8000
```

---

#### Streamlit 애플리케이션 (레거시)

```bash
# Windows
run_ui.bat

# Linux / Git Bash
bash run_ui.sh
```

**접근 URL**: `http://localhost:8501`

---

### 애플리케이션 시작 순서

1. **환경 변수 검증**
   - `CRAWLER_BASE_DIR` 환경 변수 확인
   - 필수 디렉터리 존재 여부 확인

2. **설정 로드**
   - `.env.local` (또는 `.env.prod`) 파일 로드
   - 설정값 초기화

3. **로깅 초기화**
   - 로그 디렉터리 생성
   - 로그 파일 생성 (회전 가능)

4. **데이터베이스 초기화**
   - law_summary.db 검증
   - yaml_info 테이블 로드 (필요시 생성)

5. **라우터 등록**
   - API 엔드포인트 등록
   - 정적 파일 마운팅

6. **서버 시작**
   - Uvicorn 서버 시작
   - 포트 바인딩

---

### 성능 특성

| 항목 | 값 | 비고 |
|------|-----|------|
| 메모리 사용량 | ~100-200MB | 초기 로드 |
| 응답 시간 (검색) | 100-500ms | 데이터 크기에 따라 변동 |
| 응답 시간 (통계) | 200-1000ms | 집계 작업 포함 |
| 동시 연결 | 제한 없음 | Uvicorn 기본값 |
| DB 연결 풀 | 없음 | SQLite 특성상 불필요 |

---

## 모니터링 및 로깅

### 로그 구조

#### UI 로그

**위치**: `${UI_LOG_DIR}/law_crawler.log`  
**로그 레벨**: DEBUG (또는 INFO)  
**회전 정책**:

- 파일 크기: 5MB 초과 시 회전
- 보관 파일: 최대 7개

**로그 포맷**:

```
2025-12-30 10:15:30,123 - app.backend.api.v1.search - INFO - Search executed
```

**주요 로그**:

```
[STARTUP] 애플리케이션 시작
[SHUTDOWN] 애플리케이션 종료
[API_CALL] API 호출 기록
[QUERY] 데이터베이스 쿼리
[ERROR] 오류 발생
```

---

#### Crawler 로그

**위치**: `${CRAWLER_LOG_DIR}/` 하위 `.log` 파일들  
**관리**: law-crawler 시스템 (읽기 전용)  
**용도**: 크롤링 작업 로그 조회

---

### 모니터링 포인트

#### 1. 애플리케이션 상태

- **서버 응답성**: `/` 엔드포인트 헬스 체크
- **에러 로그 모니터링**: law_crawler.log의 ERROR 레벨 로그
- **메모리 사용량**: 시스템 리소스 모니터링

#### 2. 데이터베이스 상태

- **DB 파일 크기**: `${CRAWLER_DATA_DIR}/DB/law_summary.db` 모니터링
- **쿼리 성능**: 검색/통계 쿼리 응답 시간
- **DB 무결성**: 정기적 PRAGMA integrity_check

#### 3. 첨부파일 저장소

- **디스크 용량**: `${CRAWLER_DATA_DIR}/Attaches/` 크기 모니터링
- **파일 접근성**: 첨부파일 다운로드 실패 체크

---

### 로그 분석 예시

**에러 추적**:

```bash
grep "ERROR" logs/law_crawler.log
```

**특정 모듈 추적**:

```bash
grep "app.backend.api.v1.search" logs/law_crawler.log
```

**성능 분석**:

```bash
grep "Query executed in" logs/law_crawler.log
```

---

## 배포 및 빌드

### 개발 환경

#### 준비 사항

1. **Python 설치**
   - Python >= 3.11

2. **의존성 설치**

   ```bash
   pip install -r pyproject.toml
   ```

3. **환경 변수 설정**

   ```bash
   cp env.sample .env.local
   # .env.local 파일 편집 (CRAWLER_BASE_DIR 등)
   ```

4. **개발 서버 실행**

   ```bash
   python app/backend/main.py
   ```

---

### 프로덕션 배포

#### 1. 실행 파일 생성 (Windows EXE)

```bash
# 빌드 스크립트 실행
make_exe_ui20.bat
```

**생성 결과**:

```
dist/law_crawler_ui_ui20/
├── law_crawler_ui_ui20.exe    # 메인 실행 파일
├── .env.local                  # 환경 설정 (자동 복사)
├── run.bat                     # Windows 실행 스크립트
├── run.sh                      # Linux 실행 스크립트
├── README.txt                  # 사용 가이드
├── _internal/                  # 번들 라이브러리
└── app/                        # 템플릿 및 정적 파일
```

#### 2. 배포 방법

**Option A: EXE 직접 실행**

```bash
law_crawler_ui_ui20.exe
```

**Option B: 배포 스크립트 사용**

```bash
run.bat                  # Windows
bash run.sh              # Linux/Mac
```

#### 3. 배포 전 체크리스트

- [ ] `.env.local` 파일 준비 (CRAWLER_BASE_DIR 등)
- [ ] law_summary.db 경로 확인
- [ ] LAW_SITE_DESC.yaml 경로 확인
- [ ] 로그 디렉터리 쓰기 권한 확인
- [ ] 방화벽 포트 개방 (기본값 8000)
- [ ] 테스트 실행 (pytest)

---

### 테스트

#### 테스트 실행

```bash
# 전체 테스트 실행
pytest

# 특정 테스트 파일 실행
pytest tests/test_dashboard_context.py

# 상세 출력 모드
pytest -v

# 커버리지 포함
pytest --cov=app
```

#### 테스트 구성

| 테스트 파일 | 테스트 대상 | 수량 |
|------------|-----------|------|
| test_dashboard_context.py | Dashboard 로직 | - |
| test_search_context.py | 검색 로직 | - |
| test_statistics_context.py | 통계 분석 | - |
| test_logs_context.py | 로그 조회 | - |
| test_settings_context.py | 설정 조회 | - |
| test_api.py | API 엔드포인트 | - |

---

## 주요 이슈 및 개선 사항

### 현재 제약사항

1. **인증 기능 없음**
   - 누구나 자유롭게 접근 가능
   - 내부 네트워크 전용 운영 필요
   - 향후 OAuth2/JWT 기반 인증 추가 고려

2. **SQLite 기반 단점**
   - 대규모 동시 쓰기 작업 제약
   - 복잡한 조인 쿼리 성능 저하 가능
   - 향후 PostgreSQL 등 고급 DB 검토 필요

3. **캐싱 부재**
   - 반복 검색/통계 쿼리 최적화 필요
   - 메모리 캐시 또는 Redis 도입 고려

---

### 개발 진행 사항 (v1.0 기준)

#### ✅ 완료된 사항

- [x] FastAPI 기반 웹 애플리케이션 구축
- [x] 대시보드 기능 (KPI 카드 표시)
- [x] 데이터 조회 기능
- [x] 통계 분석 기능
- [x] 로그 관리 기능
- [x] 설정 페이지
- [x] 첨부파일 다운로드
- [x] Tailwind CSS 기반 현대적 UI
- [x] Responsive Design

#### 🔄 진행 중 사항

- [ ] 로그 UI 개선 (분할 레이아웃)
- [ ] 통계 시각화 강화 (차트 고도화)
- [ ] 대시보드 KPI 세분화
- [ ] 대시보드 "렌더링 보기" 탭 개선

#### 📋 향후 계획

- [ ] 사용자 인증 기능 (OAuth2/JWT)
- [ ] 고급 검색 필터 (날짜 범위, 상태별 등)
- [ ] 데이터 내보내기 (CSV, Excel)
- [ ] 실시간 알림 (WebSocket)
- [ ] 데이터 시각화 강화 (Chart.js, D3.js)
- [ ] API 문서 자동생성 (Swagger/OpenAPI)
- [ ] 데이터베이스 마이그레이션 (PostgreSQL)
- [ ] Docker 컨테이너화
- [ ] CI/CD 파이프라인

---

### 알려진 이슈

#### 이슈 #1: 대시보드 렌더링 보기 오류

**증상**: HTML 콘텐츠가 제대로 렌더링되지 않음  
**원인**: 특수 문자/스크립트 포함 콘텐츠  
**해결책**: HTML 정제(sanitization) 추가 필요  
**상태**: 진행 중

#### 이슈 #2: 로그 파일 경로 표시

**증상**: 로그 파일 다운로드 경로가 명확하지 않음  
**원인**: UI/UX 개선 필요  
**해결책**: 파일 경로 표시 및 아이콘 추가  
**상태**: 요청됨 (prompt.md #2 참조)

#### 이슈 #3: 통계 천단위 콤마

**증상**: 일부 통계 수치에서 천단위 콤마 미처리  
**원인**: 레이아웃 미완성  
**해결책**: 통계 페이지 리디자인  
**상태**: 요청됨 (prompt.md #2 참조)

---

## 기술 지원 및 연락처

### 개발자 문서

- [개발자 가이드](CLAUDE.md) - 코드 구조 및 개발 가이드라인
- [기능 설명서](docs/기능(Ver1.0).md) - 사용자 기능 상세 설명
- [개발 요구사항](docs/prompt.md) - 개발 중인 기능 목록
- [데이터베이스 스키마](docs/table_ddl.md) - DB 구조

### 주요 연락처

- **개발팀**: [개발팀 연락처]
- **운영팀**: [운영팀 연락처]
- **법규 크롤러 담당**: law-crawler 저장소 관리자

### 문제 해결

**법규 데이터가 표시되지 않음**:

1. law_summary.db 경로 확인
2. CRAWLER_BASE_DIR 환경 변수 확인
3. 데이터베이스 무결성 검사: `sqlite3 law_summary.db "PRAGMA integrity_check;"`
4. 로그 파일 확인: `logs/law_crawler.log`

**API 응답 시간이 느린 경우**:

1. 데이터베이스 크기 확인
2. 쿼리 실행 계획 분석: `EXPLAIN QUERY PLAN`
3. 인덱스 추가 검토
4. 메모리 및 디스크 용량 확인

**첨부파일 다운로드 실패**:

1. 저장 폴더 경로 확인 (save_folder)
2. 파일 시스템 권한 확인
3. 디스크 용량 확인
4. 로그에서 구체적 오류 메시지 확인

---

## 부록: 주요 API 엔드포인트

### 대시보드 API

```
GET  /api/v1/dashboard/metrics          - 대시보드 KPI 조회
GET  /api/v1/dashboard/data              - 수집 데이터 조회
```

### 검색 API

```
GET  /api/v1/search/sites                - 사이트 목록 조회
POST /api/v1/search                      - 데이터 검색
GET  /api/v1/search/{id}                 - 상세 정보 조회
```

### 통계 API

```
GET  /api/v1/statistics/metrics          - 통계 지표 조회
GET  /api/v1/statistics/site-stats       - 사이트별 통계
GET  /api/v1/statistics/detail           - 상세 통계
```

### 로그 API

```
GET  /api/v1/logs/dates                  - 로그 날짜 목록
GET  /api/v1/logs/crawler/{date}         - Crawler 로그 조회
GET  /api/v1/logs/ui                     - UI 로그 조회
GET  /api/v1/logs/download/{filename}    - 로그 파일 다운로드
```

### 설정 API

```
GET  /api/v1/settings/system-info        - 시스템 정보 조회
GET  /api/v1/settings/sites              - 사이트 목록 조회
GET  /api/v1/settings/info-content       - Info 문서 조회
GET  /api/v1/settings/history-content    - History 문서 조회
```

### 첨부파일 API

```
GET  /api/v1/attachments                 - 첨부파일 목록 조회
GET  /api/v1/attachments/download/{id}   - 첨부파일 다운로드
```

---

## 📸 주요 화면 캡처

### 1. 📊 대시보드 (Dashboard)

![Dashboard Screenshot](images/01-dashboard.png)

**주요 특징**:

- **KPI 카드**: 오늘, 3일, 7일, 전체 수집 통계 및 오류 발생 현황
- **수집 데이터 조회**: 기간별 필터링 및 데이터 그리드 표시
- **탭 기능**: 검색결과 및 상세정보 탭으로 구분
- **실시간 현황**: 시스템 상태 및 현재 시간 표시

---

### 2. 🔍 데이터 조회 (Search)

![Search Screenshot](images/02-search.png)

**주요 특징**:

- **다중 사이트 검색**: "모든 사이트" 선택 드롭다운
- **키워드 검색**: 제목 및 요약에서 자유 텍스트 검색
- **액션 버튼**: 검색 실행 및 초기화 버튼
- **검색 결과**: 페이징 처리된 데이터 테이블 표시 (현재 결과 없음)

---

### 3. 📈 통계 분석 (Statistics)

![Statistics Screenshot](images/03-statistics.png)

**주요 특징**:

- **통계 지표**: 전체 수집 사이트(18개), 페이지(43개), 게시물(46,788), 첨부파일(75,471)
- **기간 범위**: 2025-06-09 ~ 2025-10-21
- **사이트별 수집 통계 차트**: 막대 그래프로 시각화
- **사이트별 통계 테이블**:
  - 사이트명, 게시글수, 첨부파일수 표시
  - 정렬 및 필터링 기능
  - 엑셀 다운로드 기능

---

### 4. 📋 로그 관리 (Logs)

![Logs Screenshot](images/04-logs.png)

**주요 특징**:

- **2개 탭 분리**:
  - 📋 수집(Crawler) 로그: 크롤러 실행 로그 목록
  - 🔍 UI(웹페이지) 로그: 시스템 로그 조회
- **로그 파일 목록**: 좌측에 날짜별 로그 파일 표시
- **로그 내용 뷰어**: 우측에 선택한 로그 파일의 내용 표시
- **로그 경로 표시**: `c:/law-crawler/logs\law_crawler_2025_10_21.log`
- **다운로드 기능**: 로그 파일 다운로드 아이콘

---

### 5. ⚙️ 설정 (Settings)

![Settings Screenshot](images/05-settings.png)

**주요 특징**:

- **3개 탭**:
  - 🔧 시스템 소개: 시스템 목적, 동작 방식, 대상 사이트 정보
  - 🖥️ 시스템 정보: 시스템 구성 및 상세 정보
  - 📜 시스템 History: 변경 이력 및 버전 정보
- **시스템 설명**: 법규관련 데이터 수집 목적 및 AssetErp 연동
- **대상 사이트 목록**: 18개 사이트 및 43개 페이지 정보
- **확장 가능한 구조**: 사이트 및 페이지 목록 전개 가능

---

**문서 버전**: 1.0  
**최종 수정**: 2025-12-30  
**다음 검토 예정**: 2026-03-30
