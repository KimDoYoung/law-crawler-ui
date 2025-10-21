import asyncio
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.core.logger import get_logger
from backend.core.config import config
from backend.api.endpoints.home_routes import router as home_router

from backend.core.exception_handler import add_exception_handlers


logger = get_logger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title="Law Crawler UI - 주식매매(개인용)", version="0.0.1")
    add_middlewares(app)
    add_routes(app)
    add_event_handlers(app)
    add_static_files(app)
    add_exception_handlers(app)
    return app


def add_middlewares(app: FastAPI):
    """미들웨어 설정"""
    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def add_routes(app: FastAPI):
    # API 라우터 포함
    app.include_router(home_router)
    # app.include_router(settings_router, prefix="/api/v1/settings", tags=["settings"])


def add_event_handlers(app: FastAPI):
    """이벤트 핸들러 설정"""
    app.add_event_handler("startup", startup_event)
    app.add_event_handler("shutdown", shutdown_event)


def add_static_files(app: FastAPI):
    """정적 파일 설정"""
    # static
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_files_path = os.path.join(BASE_DIR, "frontend", "public")
    app.mount("/public", StaticFiles(directory=static_files_path), name="public")


async def startup_event():
    """Law Crawler UI application  시작"""
    logger.info("---------------------------------")
    logger.info("Startup 프로세스 시작")
    logger.info("---------------------------------")

    db_path = config.DB_PATH
    parent_dir = os.path.dirname(db_path)
    # sqlite3데이터베이스 생성
    if not os.path.exists(parent_dir):
        logger.error(f"DB 디렉토리가 존재하지 않습니다. 생성합니다: {parent_dir}")

    logger.info(f"DB 파일 경로: {db_path}")
    logger.info("scheduler 시작함...")
    logger.info("---------------------------------")
    logger.info("Startup 프로세스 종료")
    logger.info("---------------------------------")


async def shutdown_event():
    """application 종료"""
    logger.info("---------------------------------")
    logger.info("Shutdown 프로세스 종료")
    logger.info("---------------------------------")


app = create_app()

if __name__ == "__main__":
    import uvicorn

    logger.info("Law Crawler UI version: " + config.VERSION)
    uvicorn.run(app, host="0.0.0.0", port=8000)
