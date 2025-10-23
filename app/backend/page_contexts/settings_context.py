"""
설정 페이지 컨텍스트 제공 함수
"""

import os
import json
from app.backend.data.db_util import yaml_info_to_html
from app.backend.core.config import config


def get_system_info():
    """
    시스템 정보 반환

    Returns:
        {
            "python_version": "3.11",
            "fastapi_version": "0.100",
            "database_type": "SQLite",
            "version": "2.0.0",
            "ui_base_dir": "/path/to/ui",
            "ui_log_dir": "/path/to/ui/logs",
            "ui_log_file": "/path/to/ui/logs/law_crawler.log",
            "crawler_base_dir": "/path/to/crawler",
            "crawler_log_dir": "/path/to/crawler/logs",
            "crawler_exe_dir": "/path/to/crawler/exe",
            "crawler_data_dir": "/path/to/crawler/data",
            "db_path": "/path/to/db/law_summary.db",
            "attachs_dir": "/path/to/Attaches",
            "yaml_path": "/path/to/LAW_SITE_DESC.yaml"
        }
    """
    return {
        "python_version": "3.11+",
        "fastapi_version": "0.100+",
        "database_type": "SQLite",
        "version": config.VERSION,
        # UI 관련 경로
        "ui_base_dir": config.UI_BASE_DIR,
        "ui_log_dir": config.UI_LOG_DIR,
        "ui_log_file": config.UI_LOG_FILE,
        # Crawler 관련 경로
        "crawler_base_dir": config.CRAWLER_BASE_DIR,
        "crawler_log_dir": config.CRAWLER_LOG_DIR,
        "crawler_exe_dir": config.CRAWLER_EXE_DIR,
        "crawler_data_dir": config.CRAWLER_DATA_DIR,
        # 파일 경로
        "db_path": config.DB_PATH,
        "attachs_dir": config.ATTACHS_DIR,
        "yaml_path": config.YAML_PATH,
    }


def get_info_content():
    """
    시스템 소개 마크다운 내용 반환

    Returns:
        마크다운 문자열
    """
    try:
        with open("app/data/info.md", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"info.md 파일을 불러올 수 없습니다: {e}"


def get_history_content():
    """
    시스템 히스토리 JSON 데이터 반환

    Returns:
        JSON 배열 (리스트)
    """
    try:
        with open("app/data/history.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return []


def get_site_list_html():
    """
    대상 사이트 및 리스트를 HTML로 반환

    Returns:
        HTML 문자열
    """
    try:
        return yaml_info_to_html()
    except Exception as e:
        return f"사이트 목록을 불러올 수 없습니다: {e}"
