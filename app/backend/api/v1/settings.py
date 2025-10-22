"""
설정 API 엔드포인트
"""
from fastapi import APIRouter
from app.backend.page_contexts.settings_context import (
    get_system_info,
    get_info_content,
    get_history_content,
    get_site_list_html
)
from app.backend.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/system-info", response_model=dict)
async def get_system_info_endpoint():
    """
    시스템 정보 조회

    Returns:
        {
            "python_version": "3.11",
            "fastapi_version": "0.100",
            "database_type": "SQLite",
            ...
        }
    """
    try:
        info = get_system_info()
        return info
    except Exception as e:
        logger.error(f"❌ 시스템 정보 조회 실패: {e}")
        return {
            "error": "시스템 정보 조회 중 오류 발생"
        }


@router.get("/info", response_model=dict)
async def get_info():
    """
    시스템 소개 콘텐츠 조회

    Returns:
        {"content": "마크다운 내용"}
    """
    try:
        content = get_info_content()
        return {"content": content}
    except Exception as e:
        logger.error(f"❌ 시스템 소개 로드 실패: {e}")
        return {"content": f"로드 실패: {e}"}


@router.get("/history", response_model=dict)
async def get_history():
    """
    시스템 히스토리 콘텐츠 조회

    Returns:
        {"content": "마크다운 내용"}
    """
    try:
        content = get_history_content()
        return {"content": content}
    except Exception as e:
        logger.error(f"❌ 시스템 히스토리 로드 실패: {e}")
        return {"content": f"로드 실패: {e}"}


@router.get("/sites", response_model=dict)
async def get_sites():
    """
    대상 사이트 목록 조회

    Returns:
        {"html": "<table>...</table>"}
    """
    try:
        html = get_site_list_html()
        return {"html": html}
    except Exception as e:
        logger.error(f"❌ 사이트 목록 조회 실패: {e}")
        return {"html": f"로드 실패: {e}"}
