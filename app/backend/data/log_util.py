"""
로그 파일 접근 유틸리티
"""
import os
from datetime import datetime
from app.backend.core.logger import get_logger
from app.backend.core.config import config

logger = get_logger(__name__)


def get_crawler_log_file_path(log_date):
    """
    크롤러 로그 파일 경로 반환

    Args:
        log_date: 로그 날짜 (datetime.date 또는 "YYYY-MM-DD" 형식)

    Returns:
        로그 파일 경로
    """
    if isinstance(log_date, datetime):
        log_date = log_date.date()

    # log_date 형식: YYYY-MM-DD or date object
    log_date_str = str(log_date).replace("-", "_")
    return os.path.join(config.LOG_DIR, f"law_crawler_{log_date_str}.log")


def get_log_data(log_date):
    """
    주어진 날짜의 크롤러 로그 데이터를 가져오는 함수

    Args:
        log_date: 로그 날짜 (datetime.date 또는 "YYYY-MM-DD" 형식)

    Returns:
        tuple: (로그 라인 리스트, 로그 파일 경로)
    """
    log_fullpath = get_crawler_log_file_path(log_date)

    if os.path.exists(log_fullpath):
        try:
            with open(log_fullpath, 'r', encoding='utf-8') as f:
                return f.readlines(), log_fullpath
        except Exception as e:
            logger.error(f"로그 파일 읽기 오류: {log_fullpath}, {e}")
            return [], log_fullpath
    else:
        logger.warning(f"로그 파일이 존재하지 않습니다: {log_fullpath}")

    return [], log_fullpath
