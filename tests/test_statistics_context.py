"""
statistics_context.py 모듈에 대한 단위 테스트
"""

import pytest
import pandas as pd
import sqlite3
from unittest.mock import Mock, patch, MagicMock

from app.backend.page_contexts.statistics_context import (
    get_statistics_metrics,
    get_site_statistics,
    get_site_file_statistics,
    get_detail_statistics,
    get_collection_period_info,
)


class TestGetStatisticsMetrics:
    """get_statistics_metrics 함수 테스트"""

    @patch("app.backend.data.db_util.get_summary_db_file")
    @patch("sqlite3.connect")
    def test_get_statistics_metrics_success(self, mock_connect, mock_get_db):
        """정상적으로 통계 메트릭 반환"""
        # Arrange
        mock_get_db.return_value = "test.db"
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # 각 쿼리에 대한 반환값 설정
        mock_cursor.fetchone.side_effect = [
            (10,),  # 전체 사이트 수
            (50,),  # 전체 페이지 수
            (1000,),  # 전체 게시물 개수
            (500,),  # 전체 첨부파일 개수
        ]

        # Act
        result = get_statistics_metrics()

        # Assert
        assert result["total_sites"] == 10
        assert result["total_pages"] == 50
        assert result["total_posts"] == 1000
        assert result["total_attachments"] == 500
        assert mock_cursor.execute.call_count == 4
        mock_conn.close.assert_called_once()

    @patch("app.backend.data.db_util.get_summary_db_file")
    @patch("sqlite3.connect")
    def test_get_statistics_metrics_zero_values(self, mock_connect, mock_get_db):
        """모든 값이 0인 경우"""
        # Arrange
        mock_get_db.return_value = "test.db"
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.side_effect = [(0,), (0,), (0,), (0,)]

        # Act
        result = get_statistics_metrics()

        # Assert
        assert result["total_sites"] == 0
        assert result["total_pages"] == 0
        assert result["total_posts"] == 0
        assert result["total_attachments"] == 0

    @patch("app.backend.data.db_util.get_summary_db_file")
    @patch("sqlite3.connect")
    def test_get_statistics_metrics_verify_queries(self, mock_connect, mock_get_db):
        """올바른 SQL 쿼리가 실행되는지 확인"""
        # Arrange
        mock_get_db.return_value = "test.db"
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.side_effect = [(5,), (10,), (100,), (50,)]

        # Act
        result = get_statistics_metrics()

        # Assert
        calls = mock_cursor.execute.call_args_list
        assert "COUNT(DISTINCT site_name)" in calls[0][0][0]
        assert "yaml_info" in calls[0][0][0]
        assert "COUNT(*)" in calls[1][0][0]
        assert "yaml_info" in calls[1][0][0]
        assert "law_summary" in calls[2][0][0]
        assert "law_summary_attach" in calls[3][0][0]


class TestGetSiteStatistics:
    """get_site_statistics 함수 테스트"""

    @patch("app.backend.page_contexts.statistics_context.site_static")
    def test_get_site_statistics_success(self, mock_site_static):
        """정상적으로 사이트별 통계 반환"""
        # Arrange
        df = pd.DataFrame({
            "사이트": ["사이트1", "사이트2", "사이트3"],
            "게시글수": [100, 200, 300],
        })
        mock_site_static.return_value = df

        # Act
        result = get_site_statistics()

        # Assert
        assert len(result) == 3
        assert result[0] == {"site": "사이트1", "count": 100}
        assert result[1] == {"site": "사이트2", "count": 200}
        assert result[2] == {"site": "사이트3", "count": 300}

    @patch("app.backend.page_contexts.statistics_context.site_static")
    def test_get_site_statistics_empty(self, mock_site_static):
        """빈 DataFrame"""
        # Arrange
        mock_site_static.return_value = pd.DataFrame()

        # Act
        result = get_site_statistics()

        # Assert
        assert result == []

    @patch("app.backend.page_contexts.statistics_context.site_static")
    def test_get_site_statistics_exception(self, mock_site_static):
        """예외 발생 시"""
        # Arrange
        mock_site_static.side_effect = Exception("Database error")

        # Act
        result = get_site_statistics()

        # Assert
        assert result == []

    @patch("app.backend.page_contexts.statistics_context.site_static")
    def test_get_site_statistics_missing_columns(self, mock_site_static):
        """일부 컬럼이 없는 경우"""
        # Arrange
        df = pd.DataFrame({
            "사이트": ["사이트1"],
        })
        mock_site_static.return_value = df

        # Act
        result = get_site_statistics()

        # Assert
        assert len(result) == 1
        assert result[0]["site"] == "사이트1"
        assert result[0]["count"] == 0  # 없는 컬럼은 0으로 처리

    @patch("app.backend.page_contexts.statistics_context.site_static")
    def test_get_site_statistics_float_values(self, mock_site_static):
        """float 값도 int로 변환"""
        # Arrange
        df = pd.DataFrame({
            "사이트": ["사이트1"],
            "게시글수": [100.5],
        })
        mock_site_static.return_value = df

        # Act
        result = get_site_statistics()

        # Assert
        assert result[0]["count"] == 100


class TestGetSiteFileStatistics:
    """get_site_file_statistics 함수 테스트"""

    @patch("app.backend.page_contexts.statistics_context.site_static_filecount")
    def test_get_site_file_statistics_success(self, mock_file_count):
        """정상적으로 첨부파일 통계 반환"""
        # Arrange
        df = pd.DataFrame({
            "사이트": ["사이트1", "사이트2"],
            "첨부파일수": [50, 100],
        })
        mock_file_count.return_value = df

        # Act
        result = get_site_file_statistics()

        # Assert
        assert len(result) == 2
        assert result[0] == {"site": "사이트1", "file_count": 50}
        assert result[1] == {"site": "사이트2", "file_count": 100}

    @patch("app.backend.page_contexts.statistics_context.site_static_filecount")
    def test_get_site_file_statistics_empty(self, mock_file_count):
        """빈 DataFrame"""
        # Arrange
        mock_file_count.return_value = pd.DataFrame()

        # Act
        result = get_site_file_statistics()

        # Assert
        assert result == []

    @patch("app.backend.page_contexts.statistics_context.site_static_filecount")
    def test_get_site_file_statistics_exception(self, mock_file_count):
        """예외 발생 시"""
        # Arrange
        mock_file_count.side_effect = Exception("Database error")

        # Act
        result = get_site_file_statistics()

        # Assert
        assert result == []

    @patch("app.backend.page_contexts.statistics_context.site_static_filecount")
    def test_get_site_file_statistics_zero_files(self, mock_file_count):
        """첨부파일이 0인 경우"""
        # Arrange
        df = pd.DataFrame({
            "사이트": ["사이트1"],
            "첨부파일수": [0],
        })
        mock_file_count.return_value = df

        # Act
        result = get_site_file_statistics()

        # Assert
        assert result[0]["file_count"] == 0


class TestGetDetailStatistics:
    """get_detail_statistics 함수 테스트"""

    @patch("app.backend.page_contexts.statistics_context.detail_static")
    def test_get_detail_statistics_success(self, mock_detail_static):
        """정상적으로 상세 통계 반환"""
        # Arrange
        df = pd.DataFrame({
            "사이트": ["사이트1", "사이트1", "사이트2"],
            "페이지": ["페이지1", "페이지2", "페이지1"],
            "게시글수": [100, 150, 200],
            "첨부파일수": [50, 75, 100],
        })
        mock_detail_static.return_value = df

        # Act
        result = get_detail_statistics()

        # Assert
        assert len(result) == 3
        assert result[0] == {
            "site": "사이트1",
            "page": "페이지1",
            "posts": 100,
            "files": 50,
        }
        assert result[1] == {
            "site": "사이트1",
            "page": "페이지2",
            "posts": 150,
            "files": 75,
        }
        assert result[2] == {
            "site": "사이트2",
            "page": "페이지1",
            "posts": 200,
            "files": 100,
        }

    @patch("app.backend.page_contexts.statistics_context.detail_static")
    def test_get_detail_statistics_empty(self, mock_detail_static):
        """빈 DataFrame"""
        # Arrange
        mock_detail_static.return_value = pd.DataFrame()

        # Act
        result = get_detail_statistics()

        # Assert
        assert result == []

    @patch("app.backend.page_contexts.statistics_context.detail_static")
    def test_get_detail_statistics_exception(self, mock_detail_static):
        """예외 발생 시"""
        # Arrange
        mock_detail_static.side_effect = Exception("Database error")

        # Act
        result = get_detail_statistics()

        # Assert
        assert result == []

    @patch("app.backend.page_contexts.statistics_context.detail_static")
    def test_get_detail_statistics_missing_columns(self, mock_detail_static):
        """일부 컬럼이 없는 경우"""
        # Arrange
        df = pd.DataFrame({
            "사이트": ["사이트1"],
            "페이지": ["페이지1"],
        })
        mock_detail_static.return_value = df

        # Act
        result = get_detail_statistics()

        # Assert
        assert len(result) == 1
        assert result[0]["site"] == "사이트1"
        assert result[0]["page"] == "페이지1"
        assert result[0]["posts"] == 0
        assert result[0]["files"] == 0

    @patch("app.backend.page_contexts.statistics_context.detail_static")
    def test_get_detail_statistics_zero_values(self, mock_detail_static):
        """게시글과 첨부파일이 0인 경우"""
        # Arrange
        df = pd.DataFrame({
            "사이트": ["사이트1"],
            "페이지": ["페이지1"],
            "게시글수": [0],
            "첨부파일수": [0],
        })
        mock_detail_static.return_value = df

        # Act
        result = get_detail_statistics()

        # Assert
        assert result[0]["posts"] == 0
        assert result[0]["files"] == 0


class TestGetCollectionPeriodInfo:
    """get_collection_period_info 함수 테스트"""

    @patch("app.backend.page_contexts.statistics_context.get_collection_period")
    def test_get_collection_period_info_success(self, mock_get_period):
        """정상적으로 수집 기간 반환"""
        # Arrange
        mock_get_period.return_value = ("2024-01-15", "2025-01-23")

        # Act
        result = get_collection_period_info()

        # Assert
        assert result["first_date"] == "2024-01-15"
        assert result["last_date"] == "2025-01-23"
        mock_get_period.assert_called_once()

    @patch("app.backend.page_contexts.statistics_context.get_collection_period")
    def test_get_collection_period_info_same_date(self, mock_get_period):
        """시작일과 종료일이 같은 경우"""
        # Arrange
        mock_get_period.return_value = ("2025-01-23", "2025-01-23")

        # Act
        result = get_collection_period_info()

        # Assert
        assert result["first_date"] == "2025-01-23"
        assert result["last_date"] == "2025-01-23"

    @patch("app.backend.page_contexts.statistics_context.get_collection_period")
    def test_get_collection_period_info_exception(self, mock_get_period):
        """예외 발생 시"""
        # Arrange
        mock_get_period.side_effect = Exception("Database error")

        # Act
        result = get_collection_period_info()

        # Assert
        assert result["first_date"] is None
        assert result["last_date"] is None

    @patch("app.backend.page_contexts.statistics_context.get_collection_period")
    def test_get_collection_period_info_none_values(self, mock_get_period):
        """None 값 반환"""
        # Arrange
        mock_get_period.return_value = (None, None)

        # Act
        result = get_collection_period_info()

        # Assert
        assert result["first_date"] is None
        assert result["last_date"] is None

    @patch("app.backend.page_contexts.statistics_context.get_collection_period")
    def test_get_collection_period_info_empty_strings(self, mock_get_period):
        """빈 문자열 반환"""
        # Arrange
        mock_get_period.return_value = ("", "")

        # Act
        result = get_collection_period_info()

        # Assert
        assert result["first_date"] == ""
        assert result["last_date"] == ""
