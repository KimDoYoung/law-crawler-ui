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
        logger.error(f"❌ 사이트 목록 로드 실패: {e}")
        return []


def search_data(site_names: list = None, keyword: str = "", page: int = 1, pagesize: int = 30):
    """
    키워드 기반 데이터 검색 (페이징 지원)

    Args:
        site_names: 선택된 사이트 코드 리스트 (None이면 전체)
        keyword: 검색 키워드 (선택사항)
        page: 페이지 번호 (1부터 시작)
        pagesize: 페이지당 항목 수

    Returns:
        {
            "items": 검색 결과,
            "total": 전체 항목 수,
            "page": 현재 페이지,
            "pagesize": 페이지당 항목 수,
            "total_pages": 전체 페이지 수
        }
    """
    try:
        # site_names가 없으면 빈 리스트 (전체 조회)
        if site_names is None or len(site_names) == 0:
            site_names = []

        # 키워드가 없고 사이트도 선택되지 않으면 빈 결과 반환
        if not keyword.strip() and len(site_names) == 0:
            return {
                "items": [],
                "total": 0,
                "page": page,
                "pagesize": pagesize,
                "total_pages": 0
            }

        df = search_law_summary(site_names=site_names, keyword=keyword)

        # 전체 항목 수 계산
        total_count = len(df)
        total_pages = (total_count + pagesize - 1) // pagesize

        # 페이지별 데이터 슬라이싱
        start_idx = (page - 1) * pagesize
        end_idx = start_idx + pagesize
        paginated_df = df.iloc[start_idx:end_idx]

        # 페이징 정보 로깅
        logger.info(f"📄 페이징: {page}/{total_pages} (전체: {total_count}건, 페이지당: {pagesize}건, 현재페이지: {len(paginated_df)}건)")

        # DataFrame을 딕셔너리 리스트로 변환
        rows = []
        for _, row in paginated_df.iterrows():
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

        return {
            "items": rows,
            "total": total_count,
            "page": page,
            "pagesize": pagesize,
            "total_pages": total_pages
        }
    except Exception as e:
        logger.error(f"❌ 검색 실패: {e}")
        return {
            "items": [],
            "total": 0,
            "page": page,
            "pagesize": pagesize,
            "total_pages": 0
        }
