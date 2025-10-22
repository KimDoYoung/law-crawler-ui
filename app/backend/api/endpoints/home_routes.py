from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse


from app.backend.core.config import config
from app.backend.core.template_engine import render_template

from app.backend.core.logger import get_logger
from app.backend.page_contexts.context_registry import PAGE_CONTEXT_PROVIDERS

logger = get_logger(__name__)

router = APIRouter()


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def display_root(request: Request):
    """루트 경로 → 대시보드로 리다이렉트"""
    return RedirectResponse(url="/dashboard")


@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def display_dashboard(request: Request):
    """대시보드 (메인 페이지)"""

    context = {
        "request": request,
        "page_path": "dashboard",
        "data": {"title": "법규관련 데이터수집 현황"},
    }
    return render_template("template/dashboard.html", context)


@router.get("/search", response_class=HTMLResponse, include_in_schema=False)
async def display_search(request: Request):
    """데이터 조회 페이지"""

    context = {
        "request": request,
        "page_path": "search",
        "data": {"title": "데이터 조회"},
    }
    return render_template("template/search.html", context)


@router.get("/statistics", response_class=HTMLResponse, include_in_schema=False)
async def display_statistics(request: Request):
    """통계 분석 페이지"""

    context = {
        "request": request,
        "page_path": "statistics",
        "data": {"title": "통계 분석"},
    }
    return render_template("template/statistics.html", context)


@router.get("/logs", response_class=HTMLResponse, include_in_schema=False)
async def display_logs(request: Request):
    """로그 관리 페이지"""

    context = {
        "request": request,
        "page_path": "logs",
        "data": {"title": "로그 관리"},
    }
    return render_template("template/logs.html", context)


@router.get("/settings", response_class=HTMLResponse, include_in_schema=False)
async def display_settings(request: Request):
    """설정 페이지"""

    context = {
        "request": request,
        "page_path": "settings",
        "data": {"title": "시스템 설정"},
    }
    return render_template("template/settings.html", context)


@router.get("/page", response_class=HTMLResponse, include_in_schema=False)
async def page(
    request: Request, path: str = Query(..., description="template폴더안의 html path")
):
    """path에 해당하는 페이지를 가져와서 보낸다."""

    # 추가적인 쿼리 파라미터를 딕셔너리로 변환
    extra_params = {k: v for k, v in request.query_params.items()}

    page_path = path.strip("/")

    context = {
        "request": request,
        "version": config.VERSION,
        "page_path": page_path,
        **extra_params,
    }

    func = PAGE_CONTEXT_PROVIDERS.get(page_path)
    if func:
        try:
            # 함수가 async인지 확인
            is_async = callable(func) and func.__code__.co_flags & 0x80

            # 함수가 매개변수를 받는지 확인
            func_params = func.__code__.co_argcount if callable(func) else 0

            if func_params > 0:
                # context를 매개변수로 전달
                data = await func(context) if is_async else func(context)
            else:
                # 매개변수가 없는 기존 함수 호환성 유지
                data = await func() if is_async else func()

            context["data"] = data
        except Exception as e:
            logger.error(f"{path}용 데이터 로딩 실패: {e}")
    else:
        data = {"title": "주식매매"}
        context["data"] = data
    template_page = f"template/{page_path}.html"
    logger.debug(f"template_page 호출됨: {template_page}")
    return render_template(template_page, context)
