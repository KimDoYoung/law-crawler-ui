import os

from dotenv import load_dotenv


class Config:
    def __init__(self):
        self.PROFILE_NAME = os.getenv("LAW_CRAWLER_MODE", "local")
        load_dotenv(dotenv_path=f".env.{self.PROFILE_NAME}")
        # Version
        self.VERSION = os.getenv("VERSION", "2.0.0")

        # TimeZone
        self.TIME_ZONE = "Asia/Seoul"

        # UI_BASE_DIR 설정
        self.UI_BASE_DIR = os.getenv("UI_BASE_DIR", "c:/law-crawler-ui")
        self.UI_LOG_DIR = os.getenv(
            "UI_LOG_DIR", os.path.join(self.UI_BASE_DIR, "logs")
        )

        # UI 로그 설정
        self.UI_LOG_LEVEL = os.getenv("UI_LOG_LEVEL", "DEBUG")
        self.UI_LOG_FILE = os.path.join(self.UI_LOG_DIR, "law_crawler.log")

        # 로그 디렉토리 생성
        if not os.path.exists(self.UI_LOG_DIR):
            os.makedirs(self.UI_LOG_DIR, exist_ok=True)

        # CRAWLER 설정
        # LAW_CRAWLER_DIR 환경 변수에서 기본 경로 읽기
        crawler_base_dir = os.getenv("CRAWLER_BASE_DIR")
        if not crawler_base_dir:
            raise ValueError("LAW_CRAWLER_DIR 환경 변수가 설정되어 있지 않습니다.")
        self.CRAWLER_BASE_DIR = crawler_base_dir

        self.CRAWLER_EXE_DIR = os.getenv(
            "CRAWLER_EXE_DIR", self.CRAWLER_BASE_DIR + "/exe"
        )
        # log dir
        self.CRAWLER_LOG_DIR = os.getenv("CRAWLER_LOG_DIR")

        self.CRAWLER_DATA_DIR = os.getenv(
            "CRAWLER_DATA_DIR", self.CRAWLER_BASE_DIR + "/data"
        )
        self.DB_PATH = os.path.join(self.CRAWLER_DATA_DIR, "DB", "law_summary.db")
        self.ATTACHS_DIR = os.path.join(self.CRAWLER_DATA_DIR, "Attaches")
        self.YAML_PATH = os.path.join(self.CRAWLER_EXE_DIR, "LAW_SITE_DESC.yaml")


config = Config()
