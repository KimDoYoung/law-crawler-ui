#!/bin/bash

# Law Crawler UI - API 테스트 스크립트
# API 목록 파일(api_list.txt)을 읽어서 자동으로 테스트합니다.

# 기본 설정
BASE_URL="${BASE_URL:-http://localhost:8004}"
API_LIST_FILE="$(dirname "$0")/api_list.txt"
RESULT_FILE="$(dirname "$0")/api_test_result.txt"
DEBUG="${DEBUG:-0}"

# 결과 카운터
TOTAL=0
PASSED=0
FAILED=0

# 결과 파일 초기화
echo "=========================================" > "$RESULT_FILE"
echo "Law Crawler UI - API 테스트 결과" >> "$RESULT_FILE"
echo "=========================================" >> "$RESULT_FILE"
echo "테스트 시간: $(date '+%Y-%m-%d %H:%M:%S')" >> "$RESULT_FILE"
echo "Base URL: $BASE_URL" >> "$RESULT_FILE"
echo "" >> "$RESULT_FILE"

echo "=========================================="
echo "Law Crawler UI - API 테스트"
echo "=========================================="
echo "Base URL: $BASE_URL"
echo "API List: $API_LIST_FILE"
echo ""

# API 목록 파일 존재 확인
if [ ! -f "$API_LIST_FILE" ]; then
    echo "❌ API 목록 파일을 찾을 수 없습니다: $API_LIST_FILE"
    exit 1
fi

# 서버 연결 확인
echo "🔍 서버 연결 확인 중..."
if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL" | grep -qE "200|302|307"; then
    echo "✅ 서버 연결 성공"
else
    echo "❌ 서버에 연결할 수 없습니다: $BASE_URL"
    echo "   서버가 실행 중인지 확인하세요."
    exit 1
fi
echo ""

echo "🚀 API 테스트 시작..."
echo "=========================================="

# API 목록 파일 읽기
while IFS='|' read -r method endpoint description; do
    # 주석과 빈 줄 건너뛰기
    [[ "$method" =~ ^#.*$ ]] && continue
    [[ -z "$method" ]] && continue

    # 공백 제거
    method=$(echo "$method" | xargs)
    endpoint=$(echo "$endpoint" | xargs)
    description=$(echo "$description" | xargs)

    TOTAL=$((TOTAL + 1))

    # API 호출
    response=$(curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$endpoint" 2>/dev/null)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    # 성공/실패 판정
    # HTTP 상태 코드가 200번대 또는 302, 307 (리다이렉트)이면 성공
    success=1

    # HTTP 코드 확인
    if ! echo "$http_code" | grep -qE "^(200|201|204|302|307)$"; then
        success=0
    fi

    # Full URL 생성
    full_url="$BASE_URL$endpoint"

    # 결과 출력 (콘솔)
    if [ $success -eq 1 ]; then
        echo "✅ $description"
        echo "   $method $endpoint (HTTP $http_code)"
        PASSED=$((PASSED + 1))

        # 결과 파일 기록 (성공)
        echo "✅ $description" >> "$RESULT_FILE"
        echo "   $full_url" >> "$RESULT_FILE"
        echo "   HTTP $http_code" >> "$RESULT_FILE"
        echo "" >> "$RESULT_FILE"

        # 디버그 모드
        if [ "$DEBUG" = "1" ]; then
            if command -v jq &> /dev/null && echo "$body" | jq -e . >/dev/null 2>&1; then
                echo "   응답: $(echo "$body" | jq -c .)"
            else
                echo "   응답: $(echo "$body" | head -c 100)..."
            fi
        fi
    else
        echo "❌ $description"
        echo "   $method $endpoint (HTTP $http_code)"

        # 결과 파일 기록 (실패)
        echo "❌ $description" >> "$RESULT_FILE"
        echo "   $full_url" >> "$RESULT_FILE"
        echo "   HTTP $http_code" >> "$RESULT_FILE"

        # 실패 시 항상 응답 일부 표시
        if command -v jq &> /dev/null && echo "$body" | jq -e . >/dev/null 2>&1; then
            error_msg=$(echo "$body" | jq -r '.error // .detail // .message // empty' 2>/dev/null)
            if [ -n "$error_msg" ]; then
                echo "   에러: $error_msg"
                echo "   에러: $error_msg" >> "$RESULT_FILE"
            else
                response_preview=$(echo "$body" | jq -c .)
                echo "   응답: $response_preview"
                echo "   응답: $response_preview" >> "$RESULT_FILE"
            fi
        else
            response_preview=$(echo "$body" | head -c 200)
            echo "   응답: $response_preview..."
            echo "   응답: $response_preview..." >> "$RESULT_FILE"
        fi
        echo "" >> "$RESULT_FILE"

        FAILED=$((FAILED + 1))
    fi

done < "$API_LIST_FILE"

echo "=========================================="
echo ""
echo "📊 테스트 결과"
echo "=========================================="
echo "총 테스트: $TOTAL"
echo "✅ 성공: $PASSED"
echo "❌ 실패: $FAILED"
echo ""

# 결과 파일에도 요약 기록
echo "=========================================" >> "$RESULT_FILE"
echo "📊 테스트 결과 요약" >> "$RESULT_FILE"
echo "=========================================" >> "$RESULT_FILE"
echo "총 테스트: $TOTAL" >> "$RESULT_FILE"
echo "✅ 성공: $PASSED" >> "$RESULT_FILE"
echo "❌ 실패: $FAILED" >> "$RESULT_FILE"
echo "" >> "$RESULT_FILE"

if [ $FAILED -eq 0 ]; then
    echo "🎉 모든 테스트 통과!"
    echo "🎉 모든 테스트 통과!" >> "$RESULT_FILE"
    echo ""
    echo "📄 상세 결과: $RESULT_FILE"
    exit 0
else
    echo "⚠️  일부 테스트 실패"
    echo "⚠️  일부 테스트 실패" >> "$RESULT_FILE"
    echo ""
    echo "📄 상세 결과: $RESULT_FILE"
    echo "💡 팁:"
    echo "  - api_list.txt에서 #을 추가하여 테스트를 건너뛸 수 있습니다"
    echo "  - BASE_URL 환경변수로 다른 서버를 테스트할 수 있습니다"
    echo "    예: BASE_URL=http://localhost:9000 ./test_api.sh"
    echo "  - 실패한 API는 위 파일에서 전체 URL을 확인할 수 있습니다"
    exit 1
fi
