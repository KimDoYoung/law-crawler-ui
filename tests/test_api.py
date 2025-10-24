"""
Law Crawler UI - API 테스트
pytest를 사용하여 모든 API 엔드포인트를 테스트합니다.

실행 방법:
    pytest tests/test_api.py -v
    pytest tests/test_api.py -v --html=report.html  # HTML 리포트
    pytest tests/test_api.py -k "dashboard"  # 특정 테스트만
"""

import os
import pytest
import requests
from typing import Dict, List


# 기본 설정
BASE_URL = os.getenv("BASE_URL", "http://localhost:8004")


class TestDashboardAPI:
    """대시보드 API 테스트"""

    def test_dashboard_metrics(self):
        """대시보드 메트릭 조회"""
        response = requests.get(f"{BASE_URL}/api/v1/dashboard/metrics")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "site_count" in data

    def test_dashboard_data_default(self):
        """대시보드 데이터 조회 (기본 period=today)"""
        response = requests.get(f"{BASE_URL}/api/v1/dashboard/data")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.parametrize("period", ["today", "3days", "7days"])
    def test_dashboard_data_with_period(self, period):
        """대시보드 데이터 조회 (period 파라미터)"""
        response = requests.get(
            f"{BASE_URL}/api/v1/dashboard/data",
            params={"period": period}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestSearchAPI:
    """검색 API 테스트"""

    def test_search_sites(self):
        """검색 가능한 사이트 목록 조회"""
        response = requests.get(f"{BASE_URL}/api/v1/search/sites")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_search_results_empty(self):
        """검색 결과 (빈 쿼리)"""
        response = requests.get(f"{BASE_URL}/api/v1/search/results")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "items" in data
        assert "total" in data

    @pytest.mark.parametrize("keyword", ["law", "test", "금융", "법률"])
    def test_search_with_keyword(self, keyword):
        """키워드 검색 (한글/영문)"""
        response = requests.get(
            f"{BASE_URL}/api/v1/search/results",
            params={"keyword": keyword}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "items" in data

    def test_search_with_pagination(self):
        """검색 결과 (페이징)"""
        response = requests.get(
            f"{BASE_URL}/api/v1/search/results",
            params={"keyword": "test", "page": 1, "pagesize": 10}
        )
        assert response.status_code == 200
        data = response.json()
        assert "page" in data
        assert "pagesize" in data
        assert data["page"] == 1
        assert data["pagesize"] == 10


class TestStatisticsAPI:
    """통계 API 테스트"""

    def test_statistics_metrics(self):
        """통계 메트릭 조회"""
        response = requests.get(f"{BASE_URL}/api/v1/statistics/metrics")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_statistics_sites(self):
        """사이트별 통계"""
        response = requests.get(f"{BASE_URL}/api/v1/statistics/sites")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_statistics_files(self):
        """파일별 통계"""
        response = requests.get(f"{BASE_URL}/api/v1/statistics/files")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_statistics_detail(self):
        """상세 통계"""
        response = requests.get(f"{BASE_URL}/api/v1/statistics/detail")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_statistics_collection_period(self):
        """수집 기간 정보"""
        response = requests.get(f"{BASE_URL}/api/v1/statistics/collection-period")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


class TestLogsAPI:
    """로그 API 테스트"""

    def test_logs_dates_default(self):
        """로그 날짜 목록 (기본 7일)"""
        response = requests.get(f"{BASE_URL}/api/v1/logs/dates")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.parametrize("days", [7, 14, 30])
    def test_logs_dates_with_days(self, days):
        """로그 날짜 목록 (days 파라미터)"""
        response = requests.get(
            f"{BASE_URL}/api/v1/logs/dates",
            params={"days": days}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_logs_ui(self):
        """UI 로그 조회"""
        response = requests.get(f"{BASE_URL}/api/v1/logs/ui")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "content" in data

    def test_logs_crawler_files(self):
        """Crawler 로그 파일 목록"""
        response = requests.get(f"{BASE_URL}/api/v1/logs/crawler/files")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestSettingsAPI:
    """설정 API 테스트"""

    def test_settings_system_info(self):
        """시스템 정보 조회"""
        response = requests.get(f"{BASE_URL}/api/v1/settings/system-info")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "version" in data

    def test_settings_info(self):
        """시스템 소개 조회"""
        response = requests.get(f"{BASE_URL}/api/v1/settings/info")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "content" in data

    def test_settings_history(self):
        """변경 이력 조회"""
        response = requests.get(f"{BASE_URL}/api/v1/settings/history")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "items" in data

    def test_settings_sites(self):
        """대상 사이트 목록 조회"""
        response = requests.get(f"{BASE_URL}/api/v1/settings/sites")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "html" in data
        assert len(data["html"]) > 0  # HTML 내용이 있는지 확인


class TestPageRoutes:
    """페이지 라우터 테스트 (HTML 응답)"""

    @pytest.mark.parametrize("path", [
        "/dashboard",
        "/search",
        "/statistics",
        "/logs",
        "/settings"
    ])
    def test_page_routes(self, path):
        """페이지 라우터 (HTML 응답 확인)"""
        response = requests.get(f"{BASE_URL}{path}")
        # 307 리다이렉트도 허용
        assert response.status_code in [200, 307]
        # HTML 응답 확인
        assert "text/html" in response.headers.get("content-type", "")


# pytest 설정
def pytest_configure(config):
    """pytest 설정"""
    config.addinivalue_line(
        "markers",
        "slow: 느린 테스트 (특정 조건에서만 실행)"
    )


if __name__ == "__main__":
    # 직접 실행시 pytest 실행
    pytest.main([__file__, "-v"])
