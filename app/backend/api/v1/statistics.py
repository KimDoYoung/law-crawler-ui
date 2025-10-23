"""
통계 분석 API 엔드포인트
"""
from fastapi import APIRouter
from app.backend.page_contexts.statistics_context import (
    get_statistics_metrics,
    get_site_statistics,
    get_site_file_statistics,
    get_detail_statistics,
    get_collection_period_info
)
from app.backend.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/statistics", tags=["statistics"])


@router.get("/metrics", response_model=dict)
async def get_metrics():
    """
    통계 메트릭 조회

    Returns:
        - total_sites: 전체 수집 사이트 수
        - total_pages: 전체 수집 페이지 수
        - today_pages: 오늘 수집 페이지 수
        - total_attachments: 전체 첨부파일 수
    """
    try:
        metrics = get_statistics_metrics()
        return metrics
    except Exception as e:
        logger.error(f"❌ 통계 메트릭 조회 실패: {e}")
        return {
            "total_sites": 0,
            "total_pages": 0,
            "today_pages": 0,
            "total_attachments": 0
        }


@router.get("/sites", response_model=list)
async def get_sites_stats():
    """
    사이트별 수집 통계 조회 (차트용)

    Returns:
        [{"site": "사이트명", "count": 100}, ...]
    """
    try:
        stats = get_site_statistics()
        return stats
    except Exception as e:
        logger.error(f"❌ 사이트 통계 조회 실패: {e}")
        return []


@router.get("/files", response_model=list)
async def get_files_stats():
    """
    사이트별 첨부파일 통계 조회

    Returns:
        [{"site": "사이트명", "file_count": 50}, ...]
    """
    try:
        stats = get_site_file_statistics()
        return stats
    except Exception as e:
        logger.error(f"❌ 첨부파일 통계 조회 실패: {e}")
        return []


@router.get("/detail", response_model=list)
async def get_detail_stats():
    """
    사이트·페이지별 상세 통계 조회

    Returns:
        [{"site": "사이트", "page": "페이지", "posts": 100, "files": 50}, ...]
    """
    try:
        stats = get_detail_statistics()
        return stats
    except Exception as e:
        logger.error(f"❌ 상세 통계 조회 실패: {e}")
        return []


@router.get("/collection-period", response_model=dict)
async def get_collection_period():
    """
    데이터 수집 기간 조회

    Returns:
        {"first_date": "2024-01-15", "last_date": "2025-01-23"}
    """
    try:
        period = get_collection_period_info()
        return period
    except Exception as e:
        logger.error(f"❌ 수집 기간 조회 실패: {e}")
        return {
            "first_date": None,
            "last_date": None
        }
