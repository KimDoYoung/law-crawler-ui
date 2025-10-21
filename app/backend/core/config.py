from dotenv import load_dotenv
import os


class Config:
    def __init__(self):
        self.PROFILE_NAME = os.getenv("LAW_CRAWLER_MODE", "local")
        load_dotenv(dotenv_path=f".env.{self.PROFILE_NAME}")
        self.VERSION = os.getenv("VERION", "2.0.0")
        # TimeZone
        self.TIME_ZONE = "Asia/Seoul"

        # BASE_DIR 설정
        self.BASE_DIR = os.getenv("BASE_DIR", "c:/law-crawler-ui/")
        self.EXE_DIR = os.getenv("LAW_CRAWLER_DIR", "c:/law-crawler/")
        self.DB_PATH = f"{self.BASE_DIR}/DB/law_summary.db"
        # 로그 설정
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
        self.LOG_DIR = os.getenv("LOG_DIR", f"{self.BASE_DIR}/logs")
        self.LOG_FILE = self.LOG_DIR + "/law_crawler.log"
        # 로그 디렉토리 생성
        log_dir = os.path.dirname(self.LOG_FILE)

        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)


config = Config()
