from dotenv import load_dotenv
import os


class Config:
    def __init__(self):
        self.PROFILE_NAME = os.getenv("LAW_CRAWLER_MODE", "local")
        load_dotenv(dotenv_path=f".env.{self.PROFILE_NAME}")
        self.VERSION = os.getenv("VERSION", "2.0.0")
        # TimeZone
        self.TIME_ZONE = "Asia/Seoul"

        # BASE_DIR 설정
        self.BASE_DIR = os.getenv("BASE_DIR", "c:/law-crawler-ui")
        # LAW_CRAWLER_DIR 환경 변수에서 기본 경로 읽기
        crawler_dir = os.getenv("LAW_CRAWLER_DIR")
        if not crawler_dir:
            raise ValueError("LAW_CRAWLER_DIR 환경 변수가 설정되어 있지 않습니다.")
        self.CRAWLER_DIR = crawler_dir
        self.CRAWLER_EXE_DIR = os.getenv(
            "LAW_CRAWLER_EXE_DIR", self.CRAWLER_DIR + "/exe"
        )

        # .env 파일 로드 (law-crawler 디렉터리에서)
        env_file = os.path.join(crawler_dir, ".env")
        if os.path.exists(env_file):
            load_dotenv(dotenv_path=env_file, override=True)

        # REPOSITORY_DIR에서 DB 경로 결정
        # repository_dir = os.getenv("REPOSITORY_DIR")
        # if repository_dir:
        #     self.DB_PATH = os.path.join(repository_dir, "DB", "law_summary.db")
        # else:
        #     self.DB_PATH = os.path.join(self.BASE_DIR, "DB", "law_summary.db")
        self.DB_PATH = os.path.join(self.CRAWLER_DIR, "DB", "law_summary.db")

        # 로그 설정
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
        self.LOG_DIR = os.getenv("LOG_DIR", os.path.join(self.BASE_DIR, "logs"))
        self.LOG_FILE = os.path.join(self.LOG_DIR, "law_crawler.log")

        # 로그 디렉토리 생성
        if not os.path.exists(self.LOG_DIR):
            os.makedirs(self.LOG_DIR, exist_ok=True)


config = Config()
