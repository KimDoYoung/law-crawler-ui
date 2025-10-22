"""
대시보드 API 엔드포인트
"""

from fastapi import APIRouter, Query
from app.backend.page_contexts.dashboard_context import (
    get_dashboard_metrics,
    get_dashboard_data,
)
from app.backend.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/metrics", response_model=dict)
async def get_metrics():
    """
    대시보드 메트릭 데이터 조회 (주요 통계)

    Returns:
        - site_count: 수집 사이트 수
        - today_collect: 오늘 수집 데이터
        - three_days_collect: 3일 수집 데이터
        - seven_days_collect: 7일 수집 데이터
        - total_collect: 전체 수집 데이터
        - error_count: 오류 발생 건수
    """
    try:
        metrics = get_dashboard_metrics()
        return metrics
    except Exception as e:
        logger.error(f"❌ 대시보드 메트릭 조회 실패: {e}")
        return {
            "site_count": "-",
            "today_collect": "-",
            "three_days_collect": "-",
            "seven_days_collect": "-",
            "total_collect": "-",
            "error_count": 0,
        }


@router.get("/data", response_model=list)
async def get_data(
    period: str = Query("today", description="기간: today, 3days, 7days"),
):
    """
    대시보드 테이블 데이터 조회

    Args:
        period: 'today' (기본값), '3days', '7days'

    Returns:
        테이블 행 리스트
    """
    try:
        data = get_dashboard_data(period)
        return data
    except Exception as e:
        logger.error(f"❌ 대시보드 데이터 조회 실패: {e}")
        return []
