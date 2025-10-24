# API 테스트 가이드

Law Crawler UI의 모든 API 엔드포인트를 테스트합니다.

## 📋 파일 구성

```
tests/
├── test_api.py           # pytest 기반 API 테스트 (권장)
├── test_api.sh           # Shell 스크립트 테스트
├── api_list.txt          # Shell 테스트용 API 목록
├── pytest.ini            # pytest 설정
├── api_test_result.txt   # Shell 테스트 결과 (자동 생성)
└── README.md             # 이 문서
```

## 🚀 빠른 시작

### pytest 사용 (권장)

```bash
# 기본 실행
pytest tests/test_api.py -v

# 특정 포트
BASE_URL=http://localhost:9000 pytest tests/test_api.py -v

# HTML 리포트 생성
pytest tests/test_api.py -v --html=report.html --self-contained-html
```

## 📖 pytest 상세 가이드

### 기본 실행

```bash
cd tests
pytest test_api.py -v
```

### 특정 테스트만 실행

```bash
# 대시보드 API만 테스트
pytest test_api.py -k "dashboard" -v

# 검색 API만 테스트
pytest test_api.py -k "search" -v

# 특정 메서드만
pytest test_api.py::TestDashboardAPI::test_dashboard_metrics -v
```

### 실패한 테스트만 재실행

```bash
# 실패한 테스트 재실행
pytest test_api.py --lf -v

# 마지막 실패부터 모두 재실행
pytest test_api.py --ff -v
```

### 리포트 생성

```bash
# HTML 리포트 (pytest-html 필요)
pytest test_api.py --html=report.html --self-contained-html

# JUnit XML 리포트 (CI/CD용)
pytest test_api.py --junitxml=report.xml

# 커버리지 리포트 (pytest-cov 필요)
pytest test_api.py --cov=app --cov-report=html
```

### 출력 제어

```bash
# 더 상세한 출력
pytest test_api.py -vv

# 간단한 출력
pytest test_api.py -q

# 실패한 테스트만 표시
pytest test_api.py --tb=short
```

### 병렬 실행 (빠른 테스트)

```bash
# pytest-xdist 필요
pytest test_api.py -n auto
```

---

## 🐚 Shell 스크립트 사용법

### 기본 실행

```bash
cd tests
./test_api.sh
```

### 다른 포트로 테스트

```bash
BASE_URL=http://localhost:9000 ./test_api.sh
```

### 원격 서버 테스트

```bash
BASE_URL=http://production-server:8000 ./test_api.sh
```

## 📝 API 목록 관리 (api_list.txt)

### 파일 형식

```
METHOD|ENDPOINT|설명
```

**예제:**
```
GET|/api/v1/dashboard/metrics|대시보드 메트릭 조회
GET|/api/v1/search/results?keyword=법률|키워드 검색 테스트
```

### 특정 API 테스트 건너뛰기

해당 줄 앞에 `#`을 추가하면 테스트를 건너뜁니다:

```
# GET|/api/v1/dashboard/metrics|대시보드 메트릭 조회  ← 이 API는 테스트 안 함
GET|/api/v1/search/sites|검색 가능한 사이트 목록  ← 이 API는 테스트함
```

### 새로운 API 추가

`api_list.txt` 파일에 새로운 줄을 추가하면 됩니다:

```
GET|/api/v1/new-endpoint|새로운 API 설명
POST|/api/v1/create|데이터 생성 API
```

## ✅ 성공/실패 판정 기준

API 테스트는 다음 조건을 **모두** 만족하면 성공으로 판정합니다:

1. **HTTP 상태 코드가 성공 범위**
   - 200, 201, 204, 302

2. **응답 본문에 "error" 문자열이 없음**
   - 대소문자 구분 없이 검사
   - JSON의 error 필드나 에러 메시지 검출

## 📊 출력 예시

### 성공 케이스

```
✅ 대시보드 메트릭 조회
   GET /api/v1/dashboard/metrics (HTTP 200)
```

### 실패 케이스

```
❌ 잘못된 엔드포인트
   GET /api/v1/invalid (HTTP 404)
   에러: Not Found
```

### 최종 결과

```
========================================
📊 테스트 결과
========================================
총 테스트: 23
✅ 성공: 20
❌ 실패: 3

⚠️  일부 테스트 실패
```

## 🔧 필수 도구

- **curl**: HTTP 요청을 위해 필요 (필수)
- **jq**: JSON 파싱을 위해 권장 (선택)

### 설치 방법

**Linux (Ubuntu/Debian):**
```bash
sudo apt install curl jq
```

**macOS:**
```bash
brew install curl jq
```

**Windows (Git Bash):**
```bash
# curl은 Git Bash에 기본 포함
# jq는 별도 설치 필요
```

## 💡 팁

### 1. 빠른 연결 테스트

서버가 실행 중인지만 확인:
```bash
curl -s http://localhost:8000
```

### 2. 특정 API만 테스트

`api_list.txt`를 백업하고 원하는 API만 남깁니다:
```bash
cp api_list.txt api_list.txt.backup
# api_list.txt를 편집하여 필요한 API만 남김
./test_api.sh
mv api_list.txt.backup api_list.txt
```

### 3. 임시 API 목록으로 테스트

```bash
cat > /tmp/test.txt << EOF
GET|/api/v1/dashboard/metrics|테스트
EOF

API_LIST_FILE=/tmp/test.txt ./test_api.sh
```

### 4. 결과를 파일로 저장

```bash
./test_api.sh > test_result.txt 2>&1
```

## 🐛 문제 해결

### "서버에 연결할 수 없습니다"

1. 서버가 실행 중인지 확인:
   ```bash
   # 서버 실행
   cd ..
   python app/backend/main.py
   ```

2. 포트 번호가 올바른지 확인

3. 방화벽 설정 확인

### "API 목록 파일을 찾을 수 없습니다"

`tests/` 폴더 안에서 실행해야 합니다:
```bash
cd tests
./test_api.sh
```

### jq 관련 경고

jq가 없어도 테스트는 정상 동작합니다. 다만 에러 메시지 파싱이 제한됩니다.

## 🔄 CI/CD 통합

GitHub Actions 또는 Jenkins에서 사용하는 예:

```yaml
# .github/workflows/api-test.yml
- name: Run API Tests
  run: |
    cd tests
    ./test_api.sh
```

## 📌 참고사항

- 모든 API는 GET 메서드를 사용합니다
- 인증이 필요한 API는 현재 지원하지 않습니다 (내부 전용 시스템)
- 페이지 라우터는 HTML 응답을 반환하므로 error 문자열 검사가 제한적일 수 있습니다
