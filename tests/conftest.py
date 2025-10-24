"""
공유 pytest fixtures 및 설정
"""

import pytest
import pandas as pd
import sqlite3
import os
from datetime import datetime, date
from unittest.mock import Mock, MagicMock, patch


@pytest.fixture
def mock_config():
    """Mock config 객체"""
    mock = Mock()
    mock.VERSION = "2.0.0"
    mock.UI_BASE_DIR = "c:/law-crawler-ui"
    mock.UI_LOG_DIR = "c:/law-crawler-ui/logs"
    mock.UI_LOG_FILE = "c:/law-crawler-ui/logs/law_crawler.log"
    mock.CRAWLER_BASE_DIR = "c:/law-crawler"
    mock.CRAWLER_LOG_DIR = "c:/law-crawler/logs"
    mock.CRAWLER_EXE_DIR = "c:/law-crawler/exe"
    mock.CRAWLER_DATA_DIR = "c:/law-crawler/data"
    mock.DB_PATH = "c:/law-crawler/data/DB/law_summary.db"
    mock.ATTACHS_DIR = "c:/law-crawler/data/Attaches"
    mock.YAML_PATH = "c:/law-crawler/exe/LAW_SITE_DESC.yaml"
    return mock


@pytest.fixture
def mock_logger():
    """Mock logger 객체"""
    logger = Mock()
    logger.debug = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    return logger


@pytest.fixture
def sample_dataframe():
    """샘플 DataFrame 생성"""
    return pd.DataFrame({
        "site_name": ["site1", "site2", "site3"],
        "page_id": ["page1", "page2", "page3"],
        "사이트": ["사이트1", "사이트2", "사이트3"],
        "페이지": ["페이지1", "페이지2", "페이지3"],
        "제목": ["제목1", "제목2", "제목3"],
        "등록일": ["2025-01-01", "2025-01-02", "2025-01-03"],
        "수집일시": ["2025-01-01 10:00:00", "2025-01-02 11:00:00", "2025-01-03 12:00:00"],
        "site_url": ["http://site1.com", "http://site2.com", "http://site3.com"],
        "detail_url": ["http://site1.com/detail1", "http://site2.com/detail2", "http://site3.com/detail3"],
        "org_url": ["http://site1.com/org1", "http://site2.com/org2", "http://site3.com/org3"],
        "summary": ["요약1", "요약2", "요약3"],
        "real_seq": [1, 2, 3],
    })


@pytest.fixture
def mock_db_connection():
    """Mock SQLite 연결 객체"""
    conn = MagicMock(spec=sqlite3.Connection)
    cursor = MagicMock(spec=sqlite3.Cursor)
    conn.cursor.return_value = cursor
    cursor.fetchone.return_value = ("2025-01-23",)
    cursor.fetchall.return_value = []
    return conn, cursor


@pytest.fixture
def mock_yaml_data():
    """샘플 YAML 데이터"""
    return {
        "site1": {
            "h_name": "사이트1",
            "url": "http://site1.com",
            "pages": [
                {"id": "page1", "desc": "페이지1", "detail_url": "/detail1"},
                {"id": "page2", "desc": "페이지2", "detail_url": "/detail2"},
            ]
        },
        "site2": {
            "h_name": "사이트2",
            "url": "http://site2.com",
            "pages": [
                {"id": "page3", "desc": "페이지3", "detail_url": "/detail3"},
            ]
        }
    }


@pytest.fixture
def temp_log_file(tmp_path):
    """임시 로그 파일 생성"""
    log_file = tmp_path / "test.log"
    log_content = """2025-01-23 10:00:00 INFO Test log line 1
2025-01-23 10:01:00 WARNING Test log line 2
2025-01-23 10:02:00 ERROR Test log line 3
"""
    log_file.write_text(log_content, encoding="utf-8")
    return str(log_file)


@pytest.fixture
def mock_get_summary_db_file():
    """get_summary_db_file 함수 mock"""
    with patch("app.backend.data.db_util.get_summary_db_file") as mock:
        mock.return_value = "c:/law-crawler/data/DB/law_summary.db"
        yield mock


@pytest.fixture
def mock_datetime_now():
    """datetime.now() mock - 고정된 날짜 반환"""
    fixed_datetime = datetime(2025, 1, 23, 12, 0, 0)
    with patch("app.backend.page_contexts.dashboard_context.datetime") as mock_dt:
        mock_dt.now.return_value = fixed_datetime
        mock_dt.strftime = datetime.strftime
        yield mock_dt


@pytest.fixture
def mock_site_dict():
    """사이트 코드-이름 매핑 딕셔너리"""
    return {
        "site1": "사이트1",
        "site2": "사이트2",
        "site3": "사이트3",
    }
