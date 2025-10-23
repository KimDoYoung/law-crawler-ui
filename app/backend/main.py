import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.backend.core.logger import get_logger
from app.backend.core.config import config
from app.backend.api.endpoints.home_routes import router as home_router
from app.backend.api.v1.dashboard import router as dashboard_router
from app.backend.api.v1.search import router as search_router
from app.backend.api.v1.statistics import router as statistics_router
from app.backend.api.v1.logs import router as logs_router
from app.backend.api.v1.settings import router as settings_router
from app.backend.api.v1.attachments import router as attachments_router
from app.backend.data.db_util import create_and_fill_yaml_table

from app.backend.core.exception_handler import add_exception_handlers


logger = get_logger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title="Law Crawler UI - 법규사이트 정보 모음", version="0.0.1")
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
    # 페이지 라우터
    app.include_router(home_router)

    # API v1 라우터
    app.include_router(dashboard_router, prefix="/api/v1")
    app.include_router(search_router, prefix="/api/v1")
    app.include_router(statistics_router, prefix="/api/v1")
    app.include_router(logs_router, prefix="/api/v1")
    app.include_router(settings_router, prefix="/api/v1")
    app.include_router(attachments_router, prefix="/api/v1")


def add_event_handlers(app: FastAPI):
    """이벤트 핸들러 설정"""
    app.add_event_handler("startup", startup_event)
    app.add_event_handler("shutdown", shutdown_event)


def add_static_files(app: FastAPI):
    """정적 파일 설정"""
    # PyInstaller로 빌드된 경우와 일반 실행을 구분
    if getattr(sys, 'frozen', False):
        # PyInstaller로 빌드된 경우
        BASE_DIR = sys._MEIPASS
        static_files_path = os.path.join(BASE_DIR, "app", "frontend", "public")
    else:
        # 일반 Python 실행
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        static_files_path = os.path.join(BASE_DIR, "frontend", "public")

    logger.info(f"Static files path: {static_files_path}")
    app.mount("/public", StaticFiles(directory=static_files_path), name="public")


async def startup_event():
    """Law Crawler UI application  시작"""
    logger.info("---------------------------------")
    logger.info("Startup 프로세스 시작")
    logger.info("---------------------------------")

    # 설정값 출력
    logger.info("[설정값 확인]")
    logger.info(f"프로필: {config.PROFILE_NAME}")
    logger.info(f"버전: {config.VERSION}")

    # 디렉토리 존재 여부 확인 함수
    def check_dir(path, name):
        exists = "✅" if os.path.exists(path) else "❌"
        status = "존재함" if os.path.exists(path) else "존재하지 않음"
        return f"{exists} {name}: {path} ({status})"

    # 파일 존재 여부 확인 함수
    def check_file(path, name):
        exists = "✅" if os.path.exists(path) else "❌"
        status = "존재함" if os.path.exists(path) else "존재하지 않음"
        return f"{exists} {name}: {path} ({status})"

    logger.info(check_dir(config.UI_BASE_DIR, "UI 기본 디렉토리"))
    logger.info(check_dir(config.UI_LOG_DIR, "UI 로그 디렉토리"))
    logger.info(check_dir(config.CRAWLER_BASE_DIR, "Crawler 기본 디렉토리"))
    logger.info(check_dir(config.CRAWLER_EXE_DIR, "Crawler 실행 디렉토리"))
    logger.info(check_dir(config.CRAWLER_DATA_DIR, "Crawler 데이터 디렉토리"))
    logger.info(check_dir(config.ATTACHS_DIR, "첨부파일 디렉토리"))
    logger.info(check_file(config.DB_PATH, "DB 파일 경로"))
    logger.info(check_file(config.YAML_PATH, "YAML 파일 경로"))
    logger.info("---------------------------------")

    db_path = config.DB_PATH
    parent_dir = os.path.dirname(db_path)
    # sqlite3데이터베이스 생성
    if not os.path.exists(parent_dir):
        logger.error(f"DB 디렉토리가 존재하지 않습니다. 생성합니다: {parent_dir}")

    logger.info(f"DB 파일 경로: {db_path}")

    # yaml_info 테이블 생성 및 YAML 데이터 로드
    try:
        create_and_fill_yaml_table(db_path, config.YAML_PATH)
        logger.info("YAML 데이터 로드 완료")
    except Exception as e:
        logger.error(f"YAML 데이터 로드 중 오류: {e}")

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
    import argparse

    # 커맨드라인 인자 파싱
    parser = argparse.ArgumentParser(description="Law Crawler UI")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port number (default: 8000)")
    args = parser.parse_args()

    logger.info("Law Crawler UI version: " + config.VERSION)
    logger.info(f"Starting server on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)
