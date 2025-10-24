"""
통계 분석 페이지 컨텍스트 제공 함수
"""
from app.backend.core.logger import get_logger
from app.backend.data.db_util import (
    site_static,
    site_static_filecount,
    detail_static,
    get_collection_period
)

logger = get_logger(__name__)


def get_statistics_metrics():
    """
    통계 메트릭 데이터 반환

    Returns:
        - total_sites: 전체 수집 사이트 수 (yaml_info의 고유 site_name 개수)
        - total_pages: 전체 수집 페이지 수 (yaml_info의 레코드 개수)
        - total_posts: 전체 게시물 개수 (law_summary 테이블의 레코드 개수)
        - total_attachments: 전체 첨부파일 개수 (law_summary_attach의 레코드 개수)
    """
    from app.backend.data.db_util import get_summary_db_file
    from sqlite3 import connect

    summary_path = get_summary_db_file()
    conn = connect(summary_path)
    cursor = conn.cursor()

    # 전체 수집 사이트 수 (yaml_info의 고유 site_name 개수)
    cursor.execute("SELECT COUNT(DISTINCT site_name) FROM yaml_info")
    total_sites = cursor.fetchone()[0]

    # 전체 수집 페이지 수 (yaml_info 테이블의 레코드 개수)
    cursor.execute("SELECT COUNT(*) FROM yaml_info")
    total_pages = cursor.fetchone()[0]

    # 전체 게시물 개수 (law_summary 테이블의 레코드 개수)
    cursor.execute("SELECT COUNT(*) FROM law_summary")
    total_posts = cursor.fetchone()[0]

    # 전체 첨부파일 개수 (law_summary_attach 테이블의 레코드 개수)
    cursor.execute("SELECT COUNT(*) FROM law_summary_attach")
    total_attachments = cursor.fetchone()[0]

    conn.close()

    logger.info(f"📊 통계 메트릭: 사이트={total_sites}, 페이지={total_pages}, 게시물={total_posts}, 첨부파일={total_attachments}")

    return {
        "total_sites": total_sites,
        "total_pages": total_pages,
        "total_posts": total_posts,
        "total_attachments": total_attachments
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


def get_collection_period_info():
    """
    데이터 수집 기간 정보 반환

    Returns:
        {"first_date": "2024-01-15", "last_date": "2025-01-23"}
    """
    try:
        first_date, last_date = get_collection_period()
        return {
            "first_date": first_date,
            "last_date": last_date
        }
    except Exception as e:
        logger.error(f"❌ 수집 기간 조회 실패: {e}")
        return {
            "first_date": None,
            "last_date": None
        }
