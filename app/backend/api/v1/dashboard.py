"""
대시보드 API 엔드포인트
"""

from fastapi import APIRouter, Query
from app.backend.page_contexts.dashboard_context import (
    get_dashboard_metrics,
    get_dashboard_data,
)
from app.backend.data.db_util import attach_list
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


@router.get("/attachments/{site_code}/{page_code}/{real_seq}")
async def get_attachments(site_code: str, page_code: str, real_seq: str):
    """
    특정 항목의 첨부파일 목록 조회

    Args:
        site_code: 사이트 코드
        page_code: 페이지 코드
        real_seq: 시퀀스 번호

    Returns:
        첨부파일 목록
    """
    try:
        attach_df = attach_list(site_code, page_code, real_seq)
        attachments_data = []

        for _, attach_row in attach_df.iterrows():
            save_file_name = attach_row.get("save_file_name", "")
            attach_url = f"/api/v1/attachments/{site_code}/{page_code}/{real_seq}/{save_file_name}"

            attachments_data.append({
                "name": save_file_name,
                "url": attach_url
            })

        return {
            "count": len(attachments_data),
            "items": attachments_data
        }
    except Exception as e:
        logger.error(f"❌ 첨부파일 조회 실패 ({site_code}/{page_code}/{real_seq}): {e}")
        return {
            "count": 0,
            "items": []
        }
