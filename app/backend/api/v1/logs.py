"""
로그 관리 API 엔드포인트
"""
from fastapi import APIRouter, Query
from app.backend.page_contexts.logs_context import (
    get_available_dates,
    get_crawler_log,
    get_ui_log
)
from app.backend.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("/dates", response_model=list)
async def get_dates(days: int = Query(7, description="과거 며칠의 날짜를 반환할지")):
    """
    사용 가능한 로그 날짜 목록 조회

    Args:
        days: 과거 며칠의 날짜를 보여줄지 (기본값: 7)

    Returns:
        [{"date": "2025-01-01", "label": "2025-01-01"}, ...]
    """
    try:
        dates = get_available_dates(days)
        return dates
    except Exception as e:
        logger.error(f"로그 날짜 조회 실패: {e}")
        return []


@router.get("/crawler", response_model=dict)
async def get_crawler(date: str = Query(..., description="로그 날짜 (YYYY-MM-DD)")):
    """
    크롤러 로그 조회

    Args:
        date: 로그 날짜 (예: 2025-01-01)

    Returns:
        {"content": "로그 내용", "path": "파일경로", "filename": "파일명"}
    """
    try:
        log_data = get_crawler_log(date)
        return log_data
    except Exception as e:
        logger.error(f"크롤러 로그 조회 실패: {e}")
        return {
            "content": f"로그 조회 중 오류 발생: {e}",
            "path": "",
            "filename": ""
        }


@router.get("/ui", response_model=dict)
async def get_ui():
    """
    UI 로그 조회

    Returns:
        {"content": "로그 내용", "path": "파일경로", "filename": "파일명"}
    """
    try:
        log_data = get_ui_log()
        return log_data
    except Exception as e:
        logger.error(f"UI 로그 조회 실패: {e}")
        return {
            "content": f"로그 조회 중 오류 발생: {e}",
            "path": "",
            "filename": ""
        }
