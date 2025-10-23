"""
데이터 조회 API 엔드포인트
"""
from fastapi import APIRouter, Query
from app.backend.page_contexts.search_context import get_sites_list, search_data
from app.backend.data.db_util import attach_list
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
        logger.error(f"❌ 사이트 목록 조회 실패: {e}")
        return []


@router.get("/results")
async def search_results(
    sites: str = Query("", description="쉼표로 구분된 사이트 코드 목록"),
    keyword: str = Query("", description="검색 키워드"),
    page: int = Query(1, description="페이지 번호 (1부터 시작)", ge=1),
    pagesize: int = Query(10, description="페이지당 항목 수", ge=10, le=100)
):
    """
    키워드 기반 데이터 검색 (페이징 지원)

    Args:
        sites: 쉼표로 구분된 사이트 코드 (예: "CODE1,CODE2"), 빈 문자열이면 모든 사이트
        keyword: 검색 키워드 (선택사항)
        page: 페이지 번호 (기본값: 1)
        pagesize: 페이지당 항목 수 (기본값: 30, 범위: 10-100)

    Returns:
        {
            "items": [검색 결과],
            "total": 전체 항목 수,
            "page": 현재 페이지,
            "pagesize": 페이지당 항목 수,
            "total_pages": 전체 페이지 수
        }
    """
    try:
        site_list = [s.strip() for s in sites.split(",") if s.strip()] if sites else []
        results = search_data(site_names=site_list, keyword=keyword, page=page, pagesize=pagesize)
        return results
    except Exception as e:
        logger.error(f"❌ 데이터 검색 실패: {e}")
        return {
            "items": [],
            "total": 0,
            "page": page,
            "pagesize": pagesize,
            "total_pages": 0
        }


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
