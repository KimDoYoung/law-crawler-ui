"""
dashboard_context.py 모듈에 대한 단위 테스트
"""

import pytest
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from app.backend.page_contexts.dashboard_context import (
    _get_latest_data_date,
    get_dashboard_metrics,
    get_dashboard_data,
)


class TestGetLatestDataDate:
    """_get_latest_data_date 함수 테스트"""

    @patch("app.backend.page_contexts.dashboard_context.get_summary_db_file")
    @patch("app.backend.page_contexts.dashboard_context.sqlite3.connect")
    def test_get_latest_data_date_success(self, mock_connect, mock_get_db):
        """정상적으로 최신 날짜를 반환하는 경우"""
        # Arrange
        mock_get_db.return_value = "test.db"
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ("2025-01-23",)

        # Act
        result = _get_latest_data_date()

        # Assert
        assert result == "2025-01-23"
        mock_cursor.execute.assert_called_once_with(
            "SELECT DATE(MAX(upd_time)) FROM law_summary"
        )
        mock_conn.close.assert_called_once()

    @patch("app.backend.page_contexts.dashboard_context.get_summary_db_file")
    @patch("app.backend.page_contexts.dashboard_context.sqlite3.connect")
    def test_get_latest_data_date_no_data(self, mock_connect, mock_get_db):
        """데이터가 없는 경우 None 반환"""
        # Arrange
        mock_get_db.return_value = "test.db"
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (None,)

        # Act
        result = _get_latest_data_date()

        # Assert
        assert result is None
        mock_conn.close.assert_called_once()

    @patch("app.backend.page_contexts.dashboard_context.get_summary_db_file")
    @patch("app.backend.page_contexts.dashboard_context.sqlite3.connect")
    def test_get_latest_data_date_exception(self, mock_connect, mock_get_db):
        """예외 발생 시 None 반환"""
        # Arrange
        mock_get_db.return_value = "test.db"
        mock_connect.side_effect = sqlite3.OperationalError("Database error")

        # Act
        result = _get_latest_data_date()

        # Assert
        assert result is None


class TestGetDashboardMetrics:
    """get_dashboard_metrics 함수 테스트"""

    @patch("app.backend.page_contexts.dashboard_context.error_count_of_last_24h")
    @patch("app.backend.page_contexts.dashboard_context.total_site_attach_counts")
    @patch("app.backend.page_contexts.dashboard_context.datetime")
    def test_get_dashboard_metrics_success(
        self, mock_datetime, mock_total_counts, mock_error_count
    ):
        """정상적으로 메트릭 데이터를 반환하는 경우"""
        # Arrange
        fixed_now = datetime(2025, 1, 23, 12, 0, 0)
        mock_datetime.now.return_value = fixed_now
        mock_datetime.strftime = datetime.strftime

        # total_site_attach_counts의 반환값 설정 (순서대로: today, 3days, 7days, first)
        mock_total_counts.side_effect = [
            (10, 20),  # today
            (30, 50),  # 3days
            (70, 100),  # 7days
            (150, 300),  # first (전체)
        ]
        mock_error_count.return_value = 5

        # Act
        result = get_dashboard_metrics()

        # Assert
        assert result["site_count"] == "150 (300)"
        assert result["today_collect"] == "10 (20)"
        assert result["three_days_collect"] == "30 (50)"
        assert result["seven_days_collect"] == "70 (100)"
        assert result["total_collect"] == "150 (300)"
        assert result["error_count"] == 5

        # total_site_attach_counts 호출 검증
        assert mock_total_counts.call_count == 4
        mock_error_count.assert_called_once()

    @patch("app.backend.page_contexts.dashboard_context.error_count_of_last_24h")
    @patch("app.backend.page_contexts.dashboard_context.total_site_attach_counts")
    @patch("app.backend.page_contexts.dashboard_context.datetime")
    def test_get_dashboard_metrics_zero_values(
        self, mock_datetime, mock_total_counts, mock_error_count
    ):
        """모든 카운트가 0인 경우"""
        # Arrange
        fixed_now = datetime(2025, 1, 23, 12, 0, 0)
        mock_datetime.now.return_value = fixed_now
        mock_datetime.strftime = datetime.strftime
        mock_total_counts.return_value = (0, 0)
        mock_error_count.return_value = 0

        # Act
        result = get_dashboard_metrics()

        # Assert
        assert result["site_count"] == "0 (0)"
        assert result["today_collect"] == "0 (0)"
        assert result["three_days_collect"] == "0 (0)"
        assert result["seven_days_collect"] == "0 (0)"
        assert result["total_collect"] == "0 (0)"
        assert result["error_count"] == 0


class TestGetDashboardData:
    """get_dashboard_data 함수 테스트"""

    @patch("app.backend.page_contexts.dashboard_context.get_summary_list")
    @patch("app.backend.page_contexts.dashboard_context.datetime")
    def test_get_dashboard_data_today(self, mock_datetime, mock_get_summary, sample_dataframe):
        """오늘 데이터 조회"""
        # Arrange
        fixed_now = datetime(2025, 1, 23, 12, 0, 0)
        mock_datetime.now.return_value = fixed_now
        mock_datetime.strftime = datetime.strftime
        mock_get_summary.return_value = sample_dataframe

        # Act
        result = get_dashboard_data(period="today")

        # Assert
        assert len(result) == 3
        assert result[0]["site_name"] == "사이트1"
        assert result[0]["page_id"] == "페이지1"
        assert result[0]["title"] == "제목1"
        assert result[0]["site_code"] == "site1"
        assert result[0]["page_code"] == "page1"

        # get_summary_list가 올바른 파라미터로 호출되었는지 확인
        mock_get_summary.assert_called_once_with("2025-01-23", None)

    @patch("app.backend.page_contexts.dashboard_context.get_summary_list")
    @patch("app.backend.page_contexts.dashboard_context.datetime")
    def test_get_dashboard_data_3days(self, mock_datetime, mock_get_summary, sample_dataframe):
        """3일 데이터 조회"""
        # Arrange
        fixed_now = datetime(2025, 1, 23, 12, 0, 0)
        mock_datetime.now.return_value = fixed_now
        mock_datetime.strftime = datetime.strftime
        mock_get_summary.return_value = sample_dataframe

        # Act
        result = get_dashboard_data(period="3days")

        # Assert
        assert len(result) == 3
        # 3일 전 (오늘 포함) ~ 오늘: 2025-01-21 ~ 2025-01-23
        mock_get_summary.assert_called_once_with("2025-01-21", "2025-01-23")

    @patch("app.backend.page_contexts.dashboard_context.get_summary_list")
    @patch("app.backend.page_contexts.dashboard_context.datetime")
    def test_get_dashboard_data_7days(self, mock_datetime, mock_get_summary, sample_dataframe):
        """7일 데이터 조회"""
        # Arrange
        fixed_now = datetime(2025, 1, 23, 12, 0, 0)
        mock_datetime.now.return_value = fixed_now
        mock_datetime.strftime = datetime.strftime
        mock_get_summary.return_value = sample_dataframe

        # Act
        result = get_dashboard_data(period="7days")

        # Assert
        assert len(result) == 3
        # 7일 전 (오늘 포함) ~ 오늘: 2025-01-17 ~ 2025-01-23
        mock_get_summary.assert_called_once_with("2025-01-17", "2025-01-23")

    @patch("app.backend.page_contexts.dashboard_context.get_summary_list")
    @patch("app.backend.page_contexts.dashboard_context.datetime")
    def test_get_dashboard_data_empty_dataframe(self, mock_datetime, mock_get_summary):
        """빈 DataFrame 반환 시"""
        # Arrange
        fixed_now = datetime(2025, 1, 23, 12, 0, 0)
        mock_datetime.now.return_value = fixed_now
        mock_datetime.strftime = datetime.strftime
        mock_get_summary.return_value = pd.DataFrame()

        # Act
        result = get_dashboard_data(period="today")

        # Assert
        assert result == []

    @patch("app.backend.page_contexts.dashboard_context.get_summary_list")
    @patch("app.backend.page_contexts.dashboard_context.datetime")
    def test_get_dashboard_data_invalid_period(self, mock_datetime, mock_get_summary, sample_dataframe):
        """잘못된 period 값 - 기본값(today) 사용"""
        # Arrange
        fixed_now = datetime(2025, 1, 23, 12, 0, 0)
        mock_datetime.now.return_value = fixed_now
        mock_datetime.strftime = datetime.strftime
        mock_get_summary.return_value = sample_dataframe

        # Act
        result = get_dashboard_data(period="invalid")

        # Assert
        assert len(result) == 3
        # 잘못된 period는 today로 처리됨
        mock_get_summary.assert_called_once_with("2025-01-23", None)

    @patch("app.backend.page_contexts.dashboard_context.get_summary_list")
    @patch("app.backend.page_contexts.dashboard_context.datetime")
    def test_get_dashboard_data_exception(self, mock_datetime, mock_get_summary):
        """예외 발생 시 빈 리스트 반환"""
        # Arrange
        fixed_now = datetime(2025, 1, 23, 12, 0, 0)
        mock_datetime.now.return_value = fixed_now
        mock_datetime.strftime = datetime.strftime
        mock_get_summary.side_effect = Exception("Database error")

        # Act
        result = get_dashboard_data(period="today")

        # Assert
        assert result == []

    @patch("app.backend.page_contexts.dashboard_context.get_summary_list")
    @patch("app.backend.page_contexts.dashboard_context.datetime")
    def test_get_dashboard_data_missing_columns(self, mock_datetime, mock_get_summary):
        """일부 컬럼이 없는 DataFrame"""
        # Arrange
        fixed_now = datetime(2025, 1, 23, 12, 0, 0)
        mock_datetime.now.return_value = fixed_now
        mock_datetime.strftime = datetime.strftime

        # 일부 컬럼만 있는 DataFrame
        partial_df = pd.DataFrame({
            "site_name": ["site1"],
            "사이트": ["사이트1"],
            "제목": ["제목1"],
        })
        mock_get_summary.return_value = partial_df

        # Act
        result = get_dashboard_data(period="today")

        # Assert
        assert len(result) == 1
        assert result[0]["site_name"] == "사이트1"
        assert result[0]["title"] == "제목1"
        # 없는 컬럼은 빈 문자열로 처리
        assert result[0]["page_id"] == ""
        assert result[0]["site_code"] == "site1"
