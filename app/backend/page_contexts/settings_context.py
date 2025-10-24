"""
설정 페이지 컨텍스트 제공 함수
"""

import os
import sys
import json
import yaml
from datetime import datetime
from app.backend.data.db_util import yaml_info_to_html
from app.backend.core.config import config


def _get_data_file_path(filename):
    """
    PyInstaller 환경에 맞는 데이터 파일 경로 반환

    Args:
        filename: 파일명 (예: "info.md")

    Returns:
        파일 전체 경로
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller로 빌드된 경우
        base_path = sys._MEIPASS
        return os.path.join(base_path, "app", "data", filename)
    else:
        # 일반 Python 실행
        return os.path.join("app", "data", filename)


def _get_site_page_count():
    """
    YAML 파일에서 사이트 수와 페이지 수 계산

    Returns:
        tuple: (site_count, page_count)
    """
    try:
        yaml_path = config.YAML_PATH
        if not os.path.exists(yaml_path):
            return (0, 0)

        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        site_count = len(data) if data else 0
        page_count = 0

        for site_name, site_info in data.items():
            pages = site_info.get('pages', [])
            page_count += len(pages)

        return (site_count, page_count)
    except Exception:
        return (0, 0)


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
    _YYYY_MM_SITE_PAGE_COMMENT_ 플레이스홀더를 현재 날짜와 YAML 데이터로 치환

    Returns:
        마크다운 문자열
    """
    try:
        file_path = _get_data_file_path("info.md")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 현재 날짜 (YYYY.MM 형식)
        current_date = datetime.now().strftime("%Y.%m")

        # YAML에서 사이트 수와 페이지 수 계산
        site_count, page_count = _get_site_page_count()

        # 플레이스홀더 치환
        replacement = f"{current_date} 현재 {site_count}개 사이트 {page_count}개 페이지"
        content = content.replace("_YYYY_MM_SITE_PAGE_COMMENT_", replacement)

        return content
    except Exception as e:
        return f"info.md 파일을 불러올 수 없습니다: {e}"


def get_history_content():
    """
    시스템 히스토리 JSON 데이터 반환

    Returns:
        JSON 배열 (리스트)
    """
    try:
        file_path = _get_data_file_path("history.json")
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
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
