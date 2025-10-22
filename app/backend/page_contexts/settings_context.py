"""
설정 페이지 컨텍스트 제공 함수
"""
import os
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
            "crawler_dir": "/path/to/crawler",
            "db_dir": "/path/to/db",
            "file_dir": "/path/to/files",
            "log_dir": "/path/to/logs"
        }
    """
    return {
        "python_version": "3.11+",
        "fastapi_version": "0.100+",
        "database_type": "SQLite",
        "crawler_dir": config.EXE_DIR,
        "db_dir": config.DB_PATH,
        "file_dir": "N/A",
        "log_dir": config.LOG_DIR,
        "version": config.VERSION
    }


def get_info_content():
    """
    시스템 소개 마크다운 내용 반환

    Returns:
        마크다운 문자열
    """
    try:
        with open("ui/data/info.md", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"info.md 파일을 불러올 수 없습니다: {e}"


def get_history_content():
    """
    시스템 히스토리 마크다운 내용 반환

    Returns:
        마크다운 문자열
    """
    try:
        with open("ui/data/history.md", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"history.md 파일을 불러올 수 없습니다: {e}"


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
