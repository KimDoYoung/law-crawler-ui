"""
logs_context.py 모듈에 대한 단위 테스트
"""

import pytest
import os
from datetime import datetime, timedelta, date
from unittest.mock import Mock, patch, MagicMock, mock_open

from app.backend.page_contexts.logs_context import (
    get_available_dates,
    get_crawler_log,
    get_ui_log,
    get_crawler_log_files,
    get_crawler_log_by_filename,
)


class TestGetAvailableDates:
    """get_available_dates 함수 테스트"""

    @patch("app.backend.page_contexts.logs_context.datetime")
    def test_get_available_dates_default(self, mock_datetime):
        """기본 7일치 날짜 목록 반환"""
        # Arrange
        fixed_now = datetime(2025, 1, 23, 12, 0, 0)
        mock_datetime.now.return_value = fixed_now

        # Act
        result = get_available_dates()

        # Assert
        assert len(result) == 7
        assert result[0] == {"date": "2025-01-23", "label": "2025-01-23"}
        assert result[6] == {"date": "2025-01-17", "label": "2025-01-17"}

    @patch("app.backend.page_contexts.logs_context.datetime")
    def test_get_available_dates_custom_days(self, mock_datetime):
        """커스텀 일수로 날짜 목록 반환"""
        # Arrange
        fixed_now = datetime(2025, 1, 23, 12, 0, 0)
        mock_datetime.now.return_value = fixed_now

        # Act
        result = get_available_dates(days_back=3)

        # Assert
        assert len(result) == 3
        assert result[0] == {"date": "2025-01-23", "label": "2025-01-23"}
        assert result[2] == {"date": "2025-01-21", "label": "2025-01-21"}

    @patch("app.backend.page_contexts.logs_context.datetime")
    def test_get_available_dates_single_day(self, mock_datetime):
        """1일치 날짜만 반환"""
        # Arrange
        fixed_now = datetime(2025, 1, 23, 12, 0, 0)
        mock_datetime.now.return_value = fixed_now

        # Act
        result = get_available_dates(days_back=1)

        # Assert
        assert len(result) == 1
        assert result[0] == {"date": "2025-01-23", "label": "2025-01-23"}


class TestGetCrawlerLog:
    """get_crawler_log 함수 테스트"""

    @patch("app.backend.page_contexts.logs_context.get_log_data")
    def test_get_crawler_log_success(self, mock_get_log_data):
        """정상적으로 로그 내용 반환"""
        # Arrange
        log_lines = [
            "2025-01-23 10:00:00 INFO Line 1\n",
            "2025-01-23 10:01:00 WARNING Line 2\n",
            "2025-01-23 10:02:00 ERROR Line 3\n",
        ]
        log_path = "c:/logs/law_crawler_2025-01-23.log"
        mock_get_log_data.return_value = (log_lines, log_path)

        # Act
        result = get_crawler_log("2025-01-23")

        # Assert
        assert result["content"] == "2025-01-23 10:00:00 INFO Line 1\n2025-01-23 10:01:00 WARNING Line 2\n2025-01-23 10:02:00 ERROR Line 3"
        assert result["path"] == log_path
        # Windows 경로 구분자를 처리
        assert result["filename"] in ["law_crawler_2025-01-23.log", "c:/logs/law_crawler_2025-01-23.log"]

        # get_log_data가 date 객체로 호출되었는지 확인
        called_date = mock_get_log_data.call_args[0][0]
        assert called_date == date(2025, 1, 23)

    @patch("app.backend.page_contexts.logs_context.get_log_data")
    def test_get_crawler_log_no_content(self, mock_get_log_data):
        """로그가 없는 경우"""
        # Arrange
        mock_get_log_data.return_value = (None, "")

        # Act
        result = get_crawler_log("2025-01-23")

        # Assert
        assert result["content"] == "해당 날짜의 로그가 없습니다."
        assert result["path"] == ""
        assert result["filename"] == ""

    @patch("app.backend.page_contexts.logs_context.get_log_data")
    def test_get_crawler_log_empty_list(self, mock_get_log_data):
        """빈 로그 리스트"""
        # Arrange
        mock_get_log_data.return_value = ([], "c:/logs/test.log")

        # Act
        result = get_crawler_log("2025-01-23")

        # Assert
        assert result["content"] == "해당 날짜의 로그가 없습니다."

    @patch("app.backend.page_contexts.logs_context.get_log_data")
    def test_get_crawler_log_exception(self, mock_get_log_data):
        """예외 발생 시"""
        # Arrange
        mock_get_log_data.side_effect = Exception("File read error")

        # Act
        result = get_crawler_log("2025-01-23")

        # Assert
        assert "로그 로드 중 오류 발생" in result["content"]
        assert result["path"] == ""
        assert result["filename"] == ""

    @patch("app.backend.page_contexts.logs_context.get_log_data")
    def test_get_crawler_log_invalid_date_format(self, mock_get_log_data):
        """잘못된 날짜 형식"""
        # Act
        result = get_crawler_log("invalid-date")

        # Assert
        assert "로그 로드 중 오류 발생" in result["content"]


class TestGetUiLog:
    """get_ui_log 함수 테스트"""

    @patch("app.backend.core.config.config")
    @patch("app.backend.page_contexts.logs_context.os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="UI Log Line 1\nUI Log Line 2\nUI Log Line 3\n")
    def test_get_ui_log_success(self, mock_file, mock_exists, mock_config):
        """정상적으로 UI 로그 반환"""
        # Arrange
        mock_config.UI_LOG_DIR = "c:/logs"
        mock_exists.return_value = True

        # Act
        result = get_ui_log()

        # Assert
        assert result["content"] == "UI Log Line 1\nUI Log Line 2\nUI Log Line 3"
        assert "law_crawler.log" in result["path"]
        assert result["filename"] == "law_crawler.log"

    @patch("app.backend.core.config.config")
    @patch("app.backend.page_contexts.logs_context.os.path.exists")
    def test_get_ui_log_file_not_exists(self, mock_exists, mock_config):
        """로그 파일이 없는 경우"""
        # Arrange
        mock_config.UI_LOG_DIR = "c:/logs"
        mock_exists.return_value = False

        # Act
        result = get_ui_log()

        # Assert
        assert result["content"] == "UI 로그가 없습니다."
        assert result["path"] == ""
        assert result["filename"] == ""

    @patch("app.backend.core.config.config")
    @patch("app.backend.page_contexts.logs_context.os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_get_ui_log_empty_file(self, mock_file, mock_exists, mock_config):
        """빈 로그 파일"""
        # Arrange
        mock_config.UI_LOG_DIR = "c:/logs"
        mock_exists.return_value = True

        # Act
        result = get_ui_log()

        # Assert
        assert result["content"] == "UI 로그가 없습니다."

    @patch("app.backend.core.config.config")
    @patch("app.backend.page_contexts.logs_context.os.path.exists")
    @patch("builtins.open")
    def test_get_ui_log_exception(self, mock_file, mock_exists, mock_config):
        """예외 발생 시"""
        # Arrange
        mock_config.UI_LOG_DIR = "c:/logs"
        mock_exists.return_value = True
        mock_file.side_effect = IOError("Cannot read file")

        # Act
        result = get_ui_log()

        # Assert
        assert "로그 로드 중 오류 발생" in result["content"]


class TestGetCrawlerLogFiles:
    """get_crawler_log_files 함수 테스트"""

    @patch("app.backend.core.config.config")
    @patch("app.backend.page_contexts.logs_context.os.path.exists")
    @patch("app.backend.page_contexts.logs_context.glob.glob")
    @patch("app.backend.page_contexts.logs_context.os.path.getmtime")
    @patch("app.backend.page_contexts.logs_context.os.path.basename")
    def test_get_crawler_log_files_success(
        self, mock_basename, mock_getmtime, mock_glob, mock_exists, mock_config
    ):
        """정상적으로 로그 파일 목록 반환"""
        # Arrange
        mock_config.CRAWLER_LOG_DIR = "c:/logs"
        mock_exists.return_value = True
        mock_glob.return_value = [
            "c:/logs/law_crawler_2025-01-23.log",
            "c:/logs/law_crawler_2025-01-22.log",
            "c:/logs/law_crawler_2025-01-21.log",
        ]
        mock_getmtime.side_effect = [
            datetime(2025, 1, 23, 10, 0, 0).timestamp(),
            datetime(2025, 1, 22, 10, 0, 0).timestamp(),
            datetime(2025, 1, 21, 10, 0, 0).timestamp(),
        ]
        mock_basename.side_effect = lambda x: x.split("/")[-1]

        # Act
        result = get_crawler_log_files()

        # Assert
        assert len(result) == 3
        # 최신 날짜 우선 정렬 확인
        assert result[0]["filename"] == "law_crawler_2025-01-23.log"
        assert result[1]["filename"] == "law_crawler_2025-01-22.log"
        assert result[2]["filename"] == "law_crawler_2025-01-21.log"
        assert result[0]["modified_time"] == "2025-01-23 10:00:00"
        # modified_timestamp는 제거되어야 함
        assert "modified_timestamp" not in result[0]

    @patch("app.backend.core.config.config")
    @patch("app.backend.page_contexts.logs_context.os.path.exists")
    def test_get_crawler_log_files_dir_not_exists(self, mock_exists, mock_config):
        """로그 디렉터리가 없는 경우"""
        # Arrange
        mock_config.CRAWLER_LOG_DIR = "c:/logs"
        mock_exists.return_value = False

        # Act
        result = get_crawler_log_files()

        # Assert
        assert result == []

    @patch("app.backend.core.config.config")
    @patch("app.backend.page_contexts.logs_context.os.path.exists")
    @patch("app.backend.page_contexts.logs_context.glob.glob")
    def test_get_crawler_log_files_no_files(self, mock_glob, mock_exists, mock_config):
        """로그 파일이 없는 경우"""
        # Arrange
        mock_config.CRAWLER_LOG_DIR = "c:/logs"
        mock_exists.return_value = True
        mock_glob.return_value = []

        # Act
        result = get_crawler_log_files()

        # Assert
        assert result == []

    @patch("app.backend.core.config.config")
    @patch("app.backend.page_contexts.logs_context.os.path.exists")
    @patch("app.backend.page_contexts.logs_context.glob.glob")
    def test_get_crawler_log_files_exception(self, mock_glob, mock_exists, mock_config):
        """예외 발생 시"""
        # Arrange
        mock_config.CRAWLER_LOG_DIR = "c:/logs"
        mock_exists.return_value = True
        mock_glob.side_effect = Exception("Glob error")

        # Act
        result = get_crawler_log_files()

        # Assert
        assert result == []


class TestGetCrawlerLogByFilename:
    """get_crawler_log_by_filename 함수 테스트"""

    @patch("app.backend.core.config.config")
    @patch("app.backend.page_contexts.logs_context.os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="Log Line 1\nLog Line 2\nLog Line 3\n")
    def test_get_crawler_log_by_filename_success(self, mock_file, mock_exists, mock_config):
        """정상적으로 로그 파일 내용 반환"""
        # Arrange
        mock_config.CRAWLER_LOG_DIR = "c:/logs"
        mock_exists.return_value = True

        # Act
        result = get_crawler_log_by_filename("law_crawler_2025-01-23.log")

        # Assert
        assert result["content"] == "Log Line 1\nLog Line 2\nLog Line 3"
        assert "law_crawler_2025-01-23.log" in result["path"]
        assert result["filename"] == "law_crawler_2025-01-23.log"

    @patch("app.backend.core.config.config")
    @patch("app.backend.page_contexts.logs_context.os.path.exists")
    def test_get_crawler_log_by_filename_not_exists(self, mock_exists, mock_config):
        """파일이 없는 경우"""
        # Arrange
        mock_config.CRAWLER_LOG_DIR = "c:/logs"
        mock_exists.return_value = False

        # Act
        result = get_crawler_log_by_filename("nonexistent.log")

        # Assert
        assert result["content"] == "해당 로그 파일이 없습니다."
        assert result["path"] == ""
        assert result["filename"] == ""

    @patch("app.backend.core.config.config")
    @patch("app.backend.page_contexts.logs_context.os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_get_crawler_log_by_filename_empty_file(self, mock_file, mock_exists, mock_config):
        """빈 파일인 경우"""
        # Arrange
        mock_config.CRAWLER_LOG_DIR = "c:/logs"
        mock_exists.return_value = True

        # Act
        result = get_crawler_log_by_filename("empty.log")

        # Assert
        assert result["content"] == "로그 내용이 없습니다."
        assert result["filename"] == "empty.log"

    @patch("app.backend.core.config.config")
    @patch("app.backend.page_contexts.logs_context.os.path.exists")
    @patch("builtins.open")
    def test_get_crawler_log_by_filename_exception(self, mock_file, mock_exists, mock_config):
        """예외 발생 시"""
        # Arrange
        mock_config.CRAWLER_LOG_DIR = "c:/logs"
        mock_exists.return_value = True
        mock_file.side_effect = IOError("Cannot read file")

        # Act
        result = get_crawler_log_by_filename("test.log")

        # Assert
        assert "로그 조회 중 오류 발생" in result["content"]
        assert result["path"] == ""
        assert result["filename"] == ""
