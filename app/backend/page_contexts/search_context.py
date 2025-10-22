"""
검색 페이지 컨텍스트 제공 함수
"""
from app.backend.core.logger import get_logger
from app.backend.data.db_util import search_law_summary, get_site_and_code_dict

logger = get_logger(__name__)


def get_sites_list():
    """
    사이트 목록 반환 (드롭다운용)

    Returns:
        [{"code": "code1", "name": "사이트명1"}, ...]
    """
    try:
        site_dict = get_site_and_code_dict()
        sites = [
            {"code": code, "name": name}
            for code, name in site_dict.items()
        ]
        return sorted(sites, key=lambda x: x["name"])
    except Exception as e:
        logger.error(f"사이트 목록 로드 실패: {e}")
        return []


def search_data(site_names: list = None, keyword: str = ""):
    """
    키워드 기반 데이터 검색

    Args:
        site_names: 선택된 사이트 코드 리스트 (None이면 전체)
        keyword: 검색 키워드

    Returns:
        검색 결과 리스트
    """
    try:
        if not keyword.strip():
            return []

        # site_names가 없으면 빈 리스트 (전체 조회)
        if site_names is None or len(site_names) == 0:
            site_names = []

        df = search_law_summary(site_names=site_names, keyword=keyword)

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
                "attachment_count": 0,
                "attachments": []
            })

        return rows
    except Exception as e:
        logger.error(f"검색 실패: {e}")
        return []
