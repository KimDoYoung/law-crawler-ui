"""
settings_context.py 모듈에 대한 단위 테스트
"""

import pytest
import sys
import os
import json
import yaml
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock, mock_open

from app.backend.page_contexts.settings_context import (
    _get_data_file_path,
    _get_site_page_count,
    get_system_info,
    get_info_content,
    get_history_content,
    get_site_list_html,
)


class TestGetDataFilePath:
    """_get_data_file_path 함수 테스트"""

    def test_get_data_file_path_normal_mode(self):
        """일반 Python 실행 모드"""
        # Arrange
        # sys.frozen이 없는 상태 (일반 실행)
        if hasattr(sys, 'frozen'):
            delattr(sys, 'frozen')

        # Act
        result = _get_data_file_path("info.md")

        # Assert
        assert result == os.path.join("app", "data", "info.md")

    @patch('sys.frozen', True, create=True)
    @patch('sys._MEIPASS', 'c:/temp/meipass', create=True)
    def test_get_data_file_path_frozen_mode(self):
        """PyInstaller로 빌드된 모드"""
        # Act
        result = _get_data_file_path("info.md")

        # Assert
        assert result == os.path.join("c:/temp/meipass", "app", "data", "info.md")

    def test_get_data_file_path_different_files(self):
        """다양한 파일명 테스트"""
        # Arrange
        if hasattr(sys, 'frozen'):
            delattr(sys, 'frozen')

        # Act & Assert
        assert _get_data_file_path("history.json").endswith("history.json")
        assert _get_data_file_path("test.txt").endswith("test.txt")


class TestGetSitePageCount:
    """_get_site_page_count 함수 테스트"""

    @patch("app.backend.page_contexts.settings_context.config")
    @patch("app.backend.page_contexts.settings_context.os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_get_site_page_count_success(self, mock_file, mock_exists, mock_config, mock_yaml_data):
        """정상적으로 사이트 및 페이지 개수 반환"""
        # Arrange
        mock_config.YAML_PATH = "test.yaml"
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = yaml.dump(mock_yaml_data)

        with patch("yaml.safe_load", return_value=mock_yaml_data):
            # Act
            site_count, page_count = _get_site_page_count()

        # Assert
        assert site_count == 2  # site1, site2
        assert page_count == 3  # page1, page2, page3

    @patch("app.backend.page_contexts.settings_context.config")
    @patch("app.backend.page_contexts.settings_context.os.path.exists")
    def test_get_site_page_count_file_not_exists(self, mock_exists, mock_config):
        """YAML 파일이 없는 경우"""
        # Arrange
        mock_config.YAML_PATH = "nonexistent.yaml"
        mock_exists.return_value = False

        # Act
        site_count, page_count = _get_site_page_count()

        # Assert
        assert site_count == 0
        assert page_count == 0

    @patch("app.backend.page_contexts.settings_context.config")
    @patch("app.backend.page_contexts.settings_context.os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_get_site_page_count_empty_yaml(self, mock_file, mock_exists, mock_config):
        """빈 YAML 파일"""
        # Arrange
        mock_config.YAML_PATH = "test.yaml"
        mock_exists.return_value = True

        with patch("yaml.safe_load", return_value=None):
            # Act
            site_count, page_count = _get_site_page_count()

        # Assert
        assert site_count == 0
        assert page_count == 0

    @patch("app.backend.page_contexts.settings_context.config")
    @patch("app.backend.page_contexts.settings_context.os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_get_site_page_count_site_no_pages(self, mock_file, mock_exists, mock_config):
        """페이지가 없는 사이트"""
        # Arrange
        mock_config.YAML_PATH = "test.yaml"
        mock_exists.return_value = True
        yaml_data = {
            "site1": {
                "h_name": "사이트1",
                "url": "http://site1.com",
                "pages": []  # 빈 페이지 리스트
            }
        }

        with patch("yaml.safe_load", return_value=yaml_data):
            # Act
            site_count, page_count = _get_site_page_count()

        # Assert
        assert site_count == 1
        assert page_count == 0

    @patch("app.backend.page_contexts.settings_context.config")
    @patch("app.backend.page_contexts.settings_context.os.path.exists")
    @patch("builtins.open")
    def test_get_site_page_count_exception(self, mock_file, mock_exists, mock_config):
        """예외 발생 시"""
        # Arrange
        mock_config.YAML_PATH = "test.yaml"
        mock_exists.return_value = True
        mock_file.side_effect = IOError("Cannot read file")

        # Act
        site_count, page_count = _get_site_page_count()

        # Assert
        assert site_count == 0
        assert page_count == 0


class TestGetSystemInfo:
    """get_system_info 함수 테스트"""

    @patch("app.backend.page_contexts.settings_context.config")
    def test_get_system_info_success(self, mock_config):
        """정상적으로 시스템 정보 반환"""
        # Arrange
        mock_config.VERSION = "2.0.0"
        mock_config.UI_BASE_DIR = "c:/law-crawler-ui"
        mock_config.UI_LOG_DIR = "c:/law-crawler-ui/logs"
        mock_config.UI_LOG_FILE = "c:/law-crawler-ui/logs/law_crawler.log"
        mock_config.CRAWLER_BASE_DIR = "c:/law-crawler"
        mock_config.CRAWLER_LOG_DIR = "c:/law-crawler/logs"
        mock_config.CRAWLER_EXE_DIR = "c:/law-crawler/exe"
        mock_config.CRAWLER_DATA_DIR = "c:/law-crawler/data"
        mock_config.DB_PATH = "c:/law-crawler/data/DB/law_summary.db"
        mock_config.ATTACHS_DIR = "c:/law-crawler/data/Attaches"
        mock_config.YAML_PATH = "c:/law-crawler/exe/LAW_SITE_DESC.yaml"

        # Act
        result = get_system_info()

        # Assert
        assert result["python_version"] == "3.11+"
        assert result["fastapi_version"] == "0.100+"
        assert result["database_type"] == "SQLite"
        assert result["version"] == "2.0.0"
        assert result["ui_base_dir"] == "c:/law-crawler-ui"
        assert result["ui_log_dir"] == "c:/law-crawler-ui/logs"
        assert result["ui_log_file"] == "c:/law-crawler-ui/logs/law_crawler.log"
        assert result["crawler_base_dir"] == "c:/law-crawler"
        assert result["crawler_log_dir"] == "c:/law-crawler/logs"
        assert result["crawler_exe_dir"] == "c:/law-crawler/exe"
        assert result["crawler_data_dir"] == "c:/law-crawler/data"
        assert result["db_path"] == "c:/law-crawler/data/DB/law_summary.db"
        assert result["attachs_dir"] == "c:/law-crawler/data/Attaches"
        assert result["yaml_path"] == "c:/law-crawler/exe/LAW_SITE_DESC.yaml"


class TestGetInfoContent:
    """get_info_content 함수 테스트"""

    @patch("app.backend.page_contexts.settings_context._get_site_page_count")
    @patch("app.backend.page_contexts.settings_context._get_data_file_path")
    @patch("builtins.open", new_callable=mock_open, read_data="시스템 소개: _YYYY_MM_SITE_PAGE_COMMENT_")
    @patch("app.backend.page_contexts.settings_context.datetime")
    def test_get_info_content_success(
        self, mock_datetime, mock_file, mock_get_path, mock_get_count
    ):
        """정상적으로 info.md 내용 반환 (플레이스홀더 치환)"""
        # Arrange
        fixed_now = datetime(2025, 1, 23, 12, 0, 0)
        mock_datetime.now.return_value = fixed_now
        mock_get_path.return_value = "app/data/info.md"
        mock_get_count.return_value = (5, 20)

        # Act
        result = get_info_content()

        # Assert
        assert "2025.01 현재 5개 사이트 20개 페이지" in result
        assert "_YYYY_MM_SITE_PAGE_COMMENT_" not in result

    @patch("app.backend.page_contexts.settings_context._get_site_page_count")
    @patch("app.backend.page_contexts.settings_context._get_data_file_path")
    @patch("builtins.open", new_callable=mock_open, read_data="일반 텍스트")
    @patch("app.backend.page_contexts.settings_context.datetime")
    def test_get_info_content_no_placeholder(
        self, mock_datetime, mock_file, mock_get_path, mock_get_count
    ):
        """플레이스홀더가 없는 경우"""
        # Arrange
        fixed_now = datetime(2025, 1, 23, 12, 0, 0)
        mock_datetime.now.return_value = fixed_now
        mock_get_path.return_value = "app/data/info.md"
        mock_get_count.return_value = (5, 20)

        # Act
        result = get_info_content()

        # Assert
        assert result == "일반 텍스트"

    @patch("app.backend.page_contexts.settings_context._get_data_file_path")
    @patch("builtins.open")
    def test_get_info_content_file_not_found(self, mock_file, mock_get_path):
        """파일이 없는 경우"""
        # Arrange
        mock_get_path.return_value = "nonexistent.md"
        mock_file.side_effect = FileNotFoundError("File not found")

        # Act
        result = get_info_content()

        # Assert
        assert "info.md 파일을 불러올 수 없습니다" in result

    @patch("app.backend.page_contexts.settings_context._get_site_page_count")
    @patch("app.backend.page_contexts.settings_context._get_data_file_path")
    @patch("builtins.open")
    def test_get_info_content_exception(self, mock_file, mock_get_path, mock_get_count):
        """예외 발생 시"""
        # Arrange
        mock_get_path.return_value = "app/data/info.md"
        mock_file.side_effect = Exception("Read error")

        # Act
        result = get_info_content()

        # Assert
        assert "info.md 파일을 불러올 수 없습니다" in result


class TestGetHistoryContent:
    """get_history_content 함수 테스트"""

    @patch("app.backend.page_contexts.settings_context._get_data_file_path")
    @patch("builtins.open", new_callable=mock_open)
    def test_get_history_content_success(self, mock_file, mock_get_path):
        """정상적으로 history.json 내용 반환"""
        # Arrange
        mock_get_path.return_value = "app/data/history.json"
        history_data = [
            {"version": "2.0.0", "date": "2025-01-23", "changes": ["변경사항1"]},
            {"version": "1.0.0", "date": "2025-01-01", "changes": ["변경사항2"]},
        ]

        with patch("json.load", return_value=history_data):
            # Act
            result = get_history_content()

        # Assert
        assert len(result) == 2
        assert result[0]["version"] == "2.0.0"
        assert result[1]["version"] == "1.0.0"

    @patch("app.backend.page_contexts.settings_context._get_data_file_path")
    @patch("builtins.open", new_callable=mock_open)
    def test_get_history_content_empty(self, mock_file, mock_get_path):
        """빈 JSON 배열"""
        # Arrange
        mock_get_path.return_value = "app/data/history.json"

        with patch("json.load", return_value=[]):
            # Act
            result = get_history_content()

        # Assert
        assert result == []

    @patch("app.backend.page_contexts.settings_context._get_data_file_path")
    @patch("builtins.open")
    def test_get_history_content_file_not_found(self, mock_file, mock_get_path):
        """파일이 없는 경우"""
        # Arrange
        mock_get_path.return_value = "nonexistent.json"
        mock_file.side_effect = FileNotFoundError("File not found")

        # Act
        result = get_history_content()

        # Assert
        assert result == []

    @patch("app.backend.page_contexts.settings_context._get_data_file_path")
    @patch("builtins.open")
    def test_get_history_content_invalid_json(self, mock_file, mock_get_path):
        """잘못된 JSON 형식"""
        # Arrange
        mock_get_path.return_value = "app/data/history.json"
        mock_file.return_value.__enter__.return_value.read.return_value = "invalid json"

        with patch("json.load", side_effect=json.JSONDecodeError("msg", "doc", 0)):
            # Act
            result = get_history_content()

        # Assert
        assert result == []


class TestGetSiteListHtml:
    """get_site_list_html 함수 테스트"""

    @patch("app.backend.page_contexts.settings_context.yaml_info_to_html")
    def test_get_site_list_html_success(self, mock_yaml_to_html):
        """정상적으로 HTML 반환"""
        # Arrange
        html_content = "<div>사이트 목록</div>"
        mock_yaml_to_html.return_value = html_content

        # Act
        result = get_site_list_html()

        # Assert
        assert result == html_content
        mock_yaml_to_html.assert_called_once()

    @patch("app.backend.page_contexts.settings_context.yaml_info_to_html")
    def test_get_site_list_html_exception(self, mock_yaml_to_html):
        """예외 발생 시"""
        # Arrange
        mock_yaml_to_html.side_effect = Exception("Database error")

        # Act
        result = get_site_list_html()

        # Assert
        assert "사이트 목록을 불러올 수 없습니다" in result

    @patch("app.backend.page_contexts.settings_context.yaml_info_to_html")
    def test_get_site_list_html_empty(self, mock_yaml_to_html):
        """빈 HTML"""
        # Arrange
        mock_yaml_to_html.return_value = ""

        # Act
        result = get_site_list_html()

        # Assert
        assert result == ""
