# config.py
"""
모듈 설명: 
    - Config 클래스: 환경 설정 및 상수 관리

작성자: 김도영
작성일: 2025-02-12
버전: 1.0
"""
import logging
import os
from dotenv import load_dotenv
from datetime import datetime

import yaml

from ui.utils.logger import setup_logger
from ui.utils.sys_util import validate_environment

logger = setup_logger()

class Settings:
    """환경 설정 및 상수 관리"""
    validate_environment()
    EXE_DIR = os.environ["LAW_CRAWLER_EXE_DIR"]

    YAML_PATH = os.path.join( EXE_DIR, "LAW_SITE_DESC.yaml")
    with open(YAML_PATH, "r", encoding='utf-8') as f:
        SITE_STRUCTURE = yaml.safe_load(f)
    ENV_PATH = os.path.join(EXE_DIR, ".env")
    logger.info(f"ENV_PATH: {ENV_PATH}")
    # .env 파일 로드
    load_dotenv(ENV_PATH, override=True, encoding='utf-8')


    REPOSITORY_DIR = os.getenv("REPOSITORY_DIR")
    DB_BASE_DIR = os.path.join(REPOSITORY_DIR, "DB") if REPOSITORY_DIR else None
    FILE_BASE_DIR = os.path.join(REPOSITORY_DIR, "Attaches") if REPOSITORY_DIR else None
    LOG_DIR = os.getenv("LOG_DIR", os.path.join(REPOSITORY_DIR, "logs")) if REPOSITORY_DIR else "logs"
    LOG_FILE_FORMAT = "%Y-%m-%d.log"  # 추가된 부분
    logger.info(f"REPOSITORY_DIR: {REPOSITORY_DIR}")
    logger.info(f"DB_BASE_DIR: {DB_BASE_DIR}")
    logger.info(f"FILE_BASE_DIR: {FILE_BASE_DIR}")
    logger.info(f"crawler LOG_DIR: {LOG_DIR}")

    @classmethod
    def get_url_of_site(cls, site_name: str) -> str:
        """사이트의 url 반환"""
        url = cls.SITE_STRUCTURE.get(site_name, {}).get('url')
        if url is None:
            raise ValueError(f"사이트 '{site_name}'에 대한 URL이 정의되어 있지 않습니다.")
        return url
    
    @classmethod
    def get_desc_by_id(cls, site: str, attr: str) -> str | None:
        """
        특정 키(key) 하위의 menu_id에 해당하는 desc 값을 반환
        예: get_desc_by_id('kofia', 'menu_4') -> '규정 제개정예고'
        """
        pages = cls.SITE_STRUCTURE.get(site, {}).get('pages', [])
        for page in pages:
            if page.get('id') == attr:
                return page.get('desc')
        return None
    
    @classmethod
    def get_db_file(cls, site_name):
        """사이트 이름에 맞는 DB 파일 경로 반환"""
        if cls.DB_BASE_DIR is None:
            raise ValueError("DB_BASE_DIR가 설정되어 있지 않습니다.")
        folder = os.path.join(cls.DB_BASE_DIR, site_name)
        os.makedirs(folder, exist_ok=True)
        return os.path.join(folder, f"{site_name}.db")
    
    @classmethod
    def get_save_folder(cls, site_name, page_id):
        """db의 save_dir에 해당"""
        if cls.FILE_BASE_DIR is None:
            raise ValueError("FILE_BASE_DIR가 설정되어 있지 않습니다.")

        folder = os.path.join(cls.FILE_BASE_DIR, site_name, page_id)
        os.makedirs(folder, exist_ok=True)
        return os.path.join(site_name, page_id)
    
    @classmethod
    def get_attach_folder(cls, site_name, page_id):
        """첨부파일 저장폴더"""
        if cls.FILE_BASE_DIR is None:
            raise ValueError("FILE_BASE_DIR가 설정되어 있지 않습니다.")
        folder = os.path.join(cls.FILE_BASE_DIR, site_name, page_id)
        os.makedirs(folder, exist_ok=True)
        return folder

    @classmethod
    def get_log_file_path(cls):
        """오늘 날짜에 맞는 로그 파일 경로 반환"""
        filename = datetime.now().strftime(cls.LOG_FILE_FORMAT)
        return os.path.join(cls.LOG_DIR, filename)
    
    @classmethod
    def get_summary_db_file(cls):
        """Summary DB 파일 경로 반환"""
        if cls.DB_BASE_DIR is None:
            raise ValueError("DB_BASE_DIR가 설정되어 있지 않습니다.")
        if not os.path.exists(cls.DB_BASE_DIR):
            os.makedirs(cls.DB_BASE_DIR, exist_ok=True)
        return os.path.join(cls.DB_BASE_DIR, "law_summary.db")
    
    @classmethod
    def get_physical_path(cls, site_name, page_id, file_name):
        """첨부파일의 전체 경로 반환"""
        if cls.FILE_BASE_DIR is None:
            raise ValueError("FILE_BASE_DIR가 설정되어 있지 않습니다.")
        folder = cls.get_attach_folder(site_name, page_id)
        return os.path.join(folder, file_name)
    
    @classmethod
    def get_crawler_log_file_path(cls, log_date):
        """주어진 날짜의 크롤러 로그 파일 경로 반환"""
        if cls.LOG_DIR is None:
            raise ValueError("LOG_DIR가 설정되어 있지 않습니다.")
        log_date = str(log_date).replace("-", "_")
        return os.path.join(cls.LOG_DIR, f"law_crawler_{log_date}.log")
# Settings에서 설정값들을 가져오고
# DbManager에서 대부분의 데이터를 sql베이스로 처리
UiConfig = Settings()
# YmalDesc = LawSiteDescriptor(UiConfig.YMAL_PATH)