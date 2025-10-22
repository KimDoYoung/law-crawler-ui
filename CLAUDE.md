# CLAUDE.md

이 문서는 **Claude Code (claude.ai/code)** 가 이 저장소의 코드를 다룰 때 참고해야 할 가이드라인을 제공합니다.

---

## 🧭 프로젝트 개요

**Law-Crawler-UI**는 법령 크롤러 시스템(`law-crawler`)에서 수집된 데이터를 조회하기 위한 **웹 기반 UI 시스템**입니다.  
처음에는 streamlit으로 가볍게 개발하였으나 사용자의 요청에 의해서 fastapi를 베이스로 다시 개발하기로 함.

이 프로젝트는 두 가지 독립된 UI 인터페이스를 제공합니다.

1. **Streamlit UI (`ui/app.py`)**  
   → 기존의 법령 데이터 조회용 인터페이스  
2. **FastAPI Web Application (`app/backend/main.py`)**  
   → 2025년 10월 21일 추가된 현대적 웹 인터페이스  
   → 이 기술스택으로 개발하는 것에 중점을 둠

> 본 시스템은 **내부 전용**으로 설계되었으며 **인증 기능은 포함되어 있지 않습니다.**

---

## ⚙️ 환경 설정

이 프로젝트는 반드시 `LAW_CRAWLER_EXE_DIR` 환경 변수가 설정되어야 합니다.  
이 경로는 **law-crawler 실행 디렉터리**를 가리켜야 하며, 아래 파일들이 포함되어야 합니다:

- `.env`
- `LAW_SITE_DESC.yaml` (사이트 구성 파일)

가상환경(`.venv`)이 존재할 경우 이를 우선 사용하며, 없으면 시스템 Python을 사용합니다.

---

## 🚀 애플리케이션 실행 방법

### Streamlit UI 실행 (기존의 방식임)

**Windows:**

```bash
run_ui.bat
```

**Linux / Git Bash:**

```bash
run_ui.sh
```

**직접 실행:**

```bash
streamlit run ui/app.py
```

---

### FastAPI 애플리케이션 실행

```bash
cd app
uvicorn app.backend.main:app --host 0.0.0.0 --port 8000
```

또는 직접 실행:

```bash
python app/backend/main.py
```

---

## 🧩 아키텍처

### 이중 UI 시스템 (Dual UI System)

이 프로젝트는 동일한 데이터 소스를 공유하는 두 개의 독립된 UI 구현체로 구성되어 있습니다.

---

### **Streamlit UI (`ui/`)**

- 단일 파일 애플리케이션: `ui/app.py` (약 497라인)
- **st-aggrid** 기반의 데이터 그리드 사용
- 메뉴 구성: Dashboard, Data Search, Statistics, Log Management, Settings
- **유틸리티 구성 (`ui/utils/`)**
  - `db_manager.py`: DB 연산 래퍼
  - `db_util.py`: 통계 및 데이터 조회용 SQL 함수
  - `ui_settings.py`: 설정 클래스
  - `logger.py`: 로깅 설정
  - `misc_utils.py`: AgGrid 설정 헬퍼 함수

---

### **FastAPI 애플리케이션 (`app/`)**

**백엔드 (`app/backend/`):**

- `main.py`: FastAPI 앱 초기화
- `core/`: 환경설정, 로깅, 템플릿 엔진, 예외 처리
- `api/endpoints/`: API 라우트 정의
- `page_contexts/`: 페이지별 컨텍스트 데이터 제공

**프론트엔드 (`app/frontend/`):**

- `views/`: Jinja2 템플릿 파일
- `public/`: 정적 리소스 (CSS, JS, 이미지 등)

**기술 스택:**

- FastAPI
- Jinja2
- TailwindCSS
- Alpine.js
- Bootstrap 의 icon을 cdn으로 포함해서 사용

---

## 🗄 데이터 저장 구조

- **데이터베이스:**  
  SQLite (`law_summary.db`) — `LAW_CRAWLER_EXE_DIR` 경로 하위
- **첨부파일:**  
  `Attaches/{site_name}/{page_id}/` 디렉터리 구조
- **로그 파일:**
  - 크롤러 로그: `{LOG_DIR}/law_crawler_{date}.log`
  - UI 로그: `{LOG_DIR}/ui.log` (또는 유사 파일)

---

## ⚙️ 설정 구조

두 UI 모두 환경 변수 기반 설정을 사용합니다.

### **Streamlit (`ui/utils/ui_settings.py`)**

- `LAW_CRAWLER_EXE_DIR` 환경 변수로부터 기본 경로를 읽음  
- `.env` 및 `LAW_SITE_DESC.yaml` 로드  
- DB, 첨부파일, 로그 경로 관련 헬퍼 제공

### **FastAPI (`app/backend/core/config.py`)**

- `.env.{PROFILE_NAME}` 패턴 사용 (기본값: `.env.local`)  
- `LAW_CRAWLER_MODE` 환경 변수로 프로필 결정

---

## 🧱 주요 설계 패턴

### Streamlit 세션 상태 관리

검색 기능은 **세션 상태(Session State)** 를 이용하여 결과를 보존합니다.

| 상태 변수 | 설명 |
|------------|------|
| `st.session_state.search_results` | 검색 결과 캐시 |
| `st.session_state.search_performed` | 검색 실행 여부 |
| `st.session_state.selected_sites` | 사용자가 선택한 사이트 목록 |
| `st.session_state.keyword` | 검색 키워드 |

---

### FastAPI 템플릿 렌더링

**컨텍스트 제공자 레지스트리 패턴**(`PAGE_CONTEXT_PROVIDERS`)을 사용합니다.  
`/page` 엔드포인트에서 `path` 파라미터를 받아 해당 경로에 맞는 컨텍스트 제공 함수를 찾아 템플릿에 데이터를 주입합니다.

---

## 🗃 데이터베이스 접근

모든 DB 조회는 `ui/utils/db_util.py` 내의 함수들을 통해 수행됩니다.

| 함수 | 설명 |
|------|------|
| `get_summary_list(date)` | 지정 날짜 이후 수집된 데이터 목록 조회 |
| `search_law_summary(site_names, keyword)` | 키워드 기반 검색 |
| `site_static()` | 사이트별 통계 조회 |
| `attach_list(site, page, seq)` | 첨부파일 목록 조회 |
| `error_count_of_last_24h()` | 최근 24시간 내 오류 건수 조회 |

---

## 📦 주요 의존성

`pyproject.toml` 내 주요 의존성:

```text
streamlit>=1.45.1
streamlit-aggrid>=1.1.5.post1
pandas>=2.3.0
numpy>=2.3.0
pyyaml>=6.0.2
python-dotenv>=1.1.0
psutil>=7.0.0
```

**Python 버전:** 3.11 이상

**uv**를 사용함(pip는 사용하지 않음)

---

## 🧰 자주 수행하는 개발 작업

### 데이터베이스 관련

- sqlite를 사용
- 1개의 database
- **docs/table_ddl.md** 참조
- **sqlite3** command 로 db를 사용가능 함.
- **c:/law-crawler/DB/law_summary.db** 가 개발시 사용하는 db임. (real에서도 같음)

DB 스키마는 **law-crawler 프로젝트에서 관리**됩니다.  
이 UI는 **읽기 전용(Read-only)** 으로 동작합니다.

- 주요 접근 테이블: 요약/본문 데이터, 첨부파일 메타데이터, 오류 로그, YAML 구성
- `DbManager.create_yaml_table()` 및 `fill_yaml()` 함수가 관련 데이터를 관리

---

### Streamlit 메뉴 추가 방법

1. `ui/app.py` 내 메뉴 선택박스(`menu`)에 새로운 옵션 추가 (약 34행 근처)
2. `elif menu == "..."` 블록 추가
3. 데이터 접근 시 `ui/utils/db_util.py` 내 함수 활용
4. `configure_aggrid()` 예제를 참고하여 AgGrid 구성 유지

---

### FastAPI 라우트 추가 방법

1. 새로운 엔드포인트를 `app/backend/api/endpoints/`에 생성하거나 기존 라우터에 추가  
2. 동적 데이터가 필요하면 `app/backend/page_contexts/context_registry.py`에 컨텍스트 제공자 등록  
3. Jinja2 템플릿을 `app/frontend/views/templates/` 디렉터리에 추가  
4. 필요한 정적 자산은 `app/frontend/public/` 디렉터리에 배치  

---

## 📁 파일 구조 참고

- `ui/data/`: Settings 메뉴에서 표시되는 Markdown 파일(`info.md`, `history.md` 등)
- 데이터베이스 파일은 이 저장소에 포함되지 않음 (law-crawler에서 제공)
- `app/`과 `ui/`는 서로 독립적인 구현체
- README.md를 제외한 모든 문서는 /docs 아래에 작성해야 함

---

## ⚠️ 중요 제약사항

- **인증/인가 없음:** 내부 신뢰 환경에서만 사용
- **읽기 전용 UI:** 수집된 데이터를 수정하지 않음
- **law-crawler 종속:** 환경 구성이 완료된 상태여야 작동
- **Windows 중심 설계:** 주요 실행 대상 플랫폼은 Windows (특히 `run_ui.bat`)
