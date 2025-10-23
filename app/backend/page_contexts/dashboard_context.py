"""
대시보드 페이지 컨텍스트 제공 함수
"""

from datetime import datetime, timedelta
from app.backend.core.logger import get_logger
from app.backend.data.db_util import (
    total_site_attach_counts,
    error_count_of_last_24h,
    get_summary_list,
    get_summary_db_file,
)
import sqlite3

logger = get_logger(__name__)


def _get_latest_data_date():
    """
    DB에서 최신 데이터의 날짜를 조회합니다.

    Returns:
        str: 최신 날짜 (YYYY-MM-DD 형식), 데이터가 없으면 None
    """
    try:
        db_path = get_summary_db_file()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT DATE(MAX(upd_time)) FROM law_summary")
        result = cursor.fetchone()
        conn.close()

        if result and result[0]:
            return result[0]
        return None
    except Exception as e:
        logger.error(f"최신 날짜 조회 실패: {e}")
        return None


def get_dashboard_metrics():
    """
    대시보드 메트릭 데이터 반환
    - 수집 사이트 수
    - 오늘/3일/7일/전체 수집 현황
    - 오류 발생 건수
    """
    # 시스템 현재 날짜 기준으로 계산
    today = datetime.now().strftime("%Y-%m-%d")
    three_days_ago = (datetime.now() - timedelta(days=2)).strftime(
        "%Y-%m-%d"
    )  # 오늘 포함 3일
    seven_days_ago = (datetime.now() - timedelta(days=6)).strftime(
        "%Y-%m-%d"
    )  # 오늘 포함 7일
    first_days_age = "1900-01-01"  # 초기 데이터 수집 시작일

    # 각 기간별 수집 데이터
    # 오늘: 특정 날짜만 (to_date=None)
    today_site_count, today_attach_count = total_site_attach_counts(today, to_date=None)
    # 3일: 3일 전 ~ 오늘
    three_site_count, three_attach_count = total_site_attach_counts(
        three_days_ago, today
    )
    # 7일: 7일 전 ~ 오늘
    seven_site_count, seven_attach_count = total_site_attach_counts(
        seven_days_ago, today
    )
    # 전체: 처음 ~ 오늘
    first_site_count, first_attach_count = total_site_attach_counts(
        first_days_age, today
    )

    # 오류 건수
    error_count = error_count_of_last_24h()

    return {
        "site_count": f"{first_site_count} ({first_attach_count})",  # 수집 사이트(pages)로 표현
        "today_collect": f"{today_site_count} ({today_attach_count})",
        "three_days_collect": f"{three_site_count} ({three_attach_count})",
        "seven_days_collect": f"{seven_site_count} ({seven_attach_count})",
        "total_collect": f"{first_site_count} ({first_attach_count})",
        "error_count": error_count,
    }


def get_dashboard_data(period: str = "today"):
    """
    대시보드 테이블 데이터 반환

    Args:
        period: 'today', '3days', '7days'

    Returns:
        테이블 행 리스트
    """
    # 시스템 현재 날짜 기준으로 계산
    today = datetime.now().strftime("%Y-%m-%d")
    three_days_ago = (datetime.now() - timedelta(days=2)).strftime(
        "%Y-%m-%d"
    )  # 오늘 포함 3일
    seven_days_ago = (datetime.now() - timedelta(days=6)).strftime(
        "%Y-%m-%d"
    )  # 오늘 포함 7일

    # 기간별 from_date, to_date 매핑
    period_map = {
        "today": (today, None),  # 오늘만
        "3days": (three_days_ago, today),  # 3일 전 ~ 오늘
        "7days": (seven_days_ago, today),  # 7일 전 ~ 오늘
    }

    from_date, to_date = period_map.get(period, (today, None))

    try:
        logger.info(
            f"대시보드 데이터 조회 시작: period={period}, from_date={from_date}, to_date={to_date}"
        )
        df = get_summary_list(from_date, to_date)
        logger.info(f"DB 조회 결과: {len(df)} rows, columns={list(df.columns)}")

        # DataFrame을 딕셔너리 리스트로 변환
        rows = []
        for _, row in df.iterrows():
            site_code = row.get("site_name", "")
            page_code = row.get("page_id", "")
            real_seq = str(row.get("real_seq", ""))

            rows.append(
                {
                    "site_name": row.get("사이트", ""),  # h_name (사이트 명칭)
                    "page_id": row.get("페이지", ""),  # desc (페이지 명칭)
                    "title": row.get("제목", ""),
                    "registration_date": row.get("등록일", ""),
                    "collection_date": row.get("수집일시", ""),
                    "site_url": row.get("site_url", ""),
                    "detail_url": row.get("detail_url", ""),
                    "org_url": row.get("org_url", ""),
                    "summary": row.get("summary", ""),
                    "real_seq": real_seq,
                    "site_code": site_code,  # 실제 코드 (첨부파일 조회용)
                    "page_code": page_code,  # 실제 코드 (첨부파일 조회용)
                }
            )
        logger.info(f"✅ 대시보드 데이터 로드 성공: {len(rows)} rows from {from_date}")
        return rows
    except Exception as e:
        logger.error(f"❌ 대시보드 데이터 로드 실패: {e}")
        import traceback

        logger.error(f"❌ 스택 트레이스: {traceback.format_exc()}")
        return []
