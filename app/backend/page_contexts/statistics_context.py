"""
통계 분석 페이지 컨텍스트 제공 함수
"""
from datetime import datetime, timedelta
from app.backend.core.logger import get_logger
from app.backend.data.db_util import (
    total_site_attach_counts,
    site_static,
    site_static_filecount,
    detail_static
)

logger = get_logger(__name__)


def get_statistics_metrics():
    """
    통계 메트릭 데이터 반환
    """
    today = datetime.now().strftime("%Y-%m-%d")

    site_count, page_count = total_site_attach_counts('1900-01-01')
    today_count, today_attach = total_site_attach_counts(today)

    return {
        "total_sites": site_count,
        "total_pages": page_count,
        "today_pages": today_count,
        "total_attachments": page_count
    }


def get_site_statistics():
    """
    사이트별 수집 통계 반환 (차트용)

    Returns:
        [{"site": "사이트명", "count": 100}, ...]
    """
    try:
        df = site_static()
        rows = []
        for _, row in df.iterrows():
            rows.append({
                "site": row.get("사이트", ""),
                "count": int(row.get("게시글수", 0))
            })
        return rows
    except Exception as e:
        logger.error(f"❌ 사이트별 통계 로드 실패: {e}")
        return []


def get_site_file_statistics():
    """
    사이트별 첨부파일 통계 반환

    Returns:
        [{"site": "사이트명", "file_count": 50}, ...]
    """
    try:
        df = site_static_filecount()
        rows = []
        for _, row in df.iterrows():
            rows.append({
                "site": row.get("사이트", ""),
                "file_count": int(row.get("첨부파일수", 0))
            })
        return rows
    except Exception as e:
        logger.error(f"❌ 사이트별 첨부파일 통계 로드 실패: {e}")
        return []


def get_detail_statistics():
    """
    사이트·페이지별 상세 통계 반환

    Returns:
        [{"site": "사이트", "page": "페이지", "posts": 100, "files": 50}, ...]
    """
    try:
        df = detail_static()
        rows = []
        for _, row in df.iterrows():
            rows.append({
                "site": row.get("사이트", ""),
                "page": row.get("페이지", ""),
                "posts": int(row.get("게시글수", 0)),
                "files": int(row.get("첨부파일수", 0))
            })
        return rows
    except Exception as e:
        logger.error(f"❌ 상세 통계 로드 실패: {e}")
        return []
