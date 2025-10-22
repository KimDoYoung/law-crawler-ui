"""
대시보드 페이지 컨텍스트 제공 함수
"""
from datetime import datetime, timedelta
from app.backend.core.logger import get_logger
from app.backend.data.db_util import (
    total_site_attach_counts,
    error_count_of_last_24h,
    get_summary_list
)

logger = get_logger(__name__)


def get_dashboard_metrics():
    """
    대시보드 메트릭 데이터 반환
    - 수집 사이트 수
    - 오늘/3일/7일/전체 수집 현황
    - 오류 발생 건수
    """
    today = datetime.now().strftime("%Y-%m-%d")
    three_days_ago = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    first_days_age = '1900-01-01'  # 초기 데이터 수집 시작일

    # 각 기간별 수집 데이터
    today_site_count, today_attach_count = total_site_attach_counts(today)
    three_site_count, three_attach_count = total_site_attach_counts(three_days_ago)
    seven_site_count, seven_attach_count = total_site_attach_counts(seven_days_ago)
    first_site_count, first_attach_count = total_site_attach_counts(first_days_age)

    # 오류 건수
    error_count = error_count_of_last_24h()

    return {
        "site_count": f"{first_site_count} ({first_attach_count})",  # 수집 사이트(pages)로 표현
        "today_collect": f"{today_site_count} ({today_attach_count})",
        "three_days_collect": f"{three_site_count} ({three_attach_count})",
        "seven_days_collect": f"{seven_site_count} ({seven_attach_count})",
        "total_collect": f"{first_site_count} ({first_attach_count})",
        "error_count": error_count
    }


def get_dashboard_data(period: str = "today"):
    """
    대시보드 테이블 데이터 반환

    Args:
        period: 'today', '3days', '7days'

    Returns:
        테이블 행 리스트
    """
    today = datetime.now().strftime("%Y-%m-%d")
    three_days_ago = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    period_map = {
        "today": today,
        "3days": three_days_ago,
        "7days": seven_days_ago,
    }

    from_date = period_map.get(period, today)

    try:
        df = get_summary_list(from_date)

        # DataFrame을 딕셔너리 리스트로 변환
        rows = []
        for _, row in df.iterrows():
            rows.append({
                "site_name": row.get("사이트", ""),
                "page_id": row.get("페이지", ""),
                "title": row.get("제목", ""),
                "registration_date": row.get("등록일", ""),
                "collection_date": row.get("수집일시", ""),
                "site_url": row.get("site_url", ""),
                "detail_url": row.get("detail_url", ""),
                "org_url": row.get("org_url", ""),
                "summary": row.get("summary", ""),
                "attachment_count": 0,  # 나중에 첨부파일 개수 로드
                "attachments": []  # 나중에 첨부파일 정보 로드
            })

        return rows
    except Exception as e:
        logger.error(f"❌ 대시보드 데이터 로드 실패: {e}")
        return []
