"""
데이터 조회 API 엔드포인트
"""
from fastapi import APIRouter, Query
from app.backend.page_contexts.search_context import get_sites_list, search_data
from app.backend.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/sites", response_model=list)
async def get_sites():
    """
    사이트 목록 조회

    Returns:
        [{"code": "code1", "name": "사이트명1"}, ...]
    """
    try:
        sites = get_sites_list()
        return sites
    except Exception as e:
        logger.error(f"사이트 목록 조회 실패: {e}")
        return []


@router.get("/results", response_model=list)
async def search_results(
    sites: str = Query("", description="쉼표로 구분된 사이트 코드 목록"),
    keyword: str = Query("", description="검색 키워드")
):
    """
    키워드 기반 데이터 검색

    Args:
        sites: 쉼표로 구분된 사이트 코드 (예: "CODE1,CODE2")
        keyword: 검색 키워드

    Returns:
        검색 결과 리스트
    """
    try:
        site_list = [s.strip() for s in sites.split(",") if s.strip()] if sites else []
        results = search_data(site_names=site_list, keyword=keyword)
        return results
    except Exception as e:
        logger.error(f"데이터 검색 실패: {e}")
        return []
