import sqlite3
import yaml
import threading

from ui.utils.logger import setup_logger
from ui.utils.ui_settings import Settings

logger = setup_logger()

class DbManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, config: Settings):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DbManager, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self, config: Settings):
        if self._initialized:
            return

        # config 처리
        self.config = config
        if not self.config.DB_BASE_DIR:
            raise ValueError("DB_BASE_DIR 설정이 필요합니다.")
        self.summary_path = self.config.DB_BASE_DIR + "/law_summary.db"
        self.yaml_info = "yaml_info"
        
        # 캐시된 데이터
        self._yaml_data_cache = None
        self._site_count = None
        self._page_count = None

        self._initialized = True

    def create_yaml_table(self):
        try:
            conn = sqlite3.connect(self.summary_path)
            cursor = conn.cursor()
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.yaml_info} (
                    site_name TEXT NOT NULL,
                    page_id TEXT NOT NULL,
                    h_name TEXT,
                    desc TEXT,
                    url TEXT,
                    detail_url TEXT,
                    PRIMARY KEY (site_name, page_id)
                );
            """)
            conn.commit()
            logger.info(f"{self.yaml_info} 테이블 생성 완료")
        except Exception as e:
            logger.error(f"{self.yaml_info} 테이블 생성 오류: {e}")
            conn.rollback()
        finally:
            if conn:
                conn.close()

    def fill_yaml(self):        
        try:
            with sqlite3.connect(self.summary_path) as conn:
                cursor = conn.cursor()
                
                # 기존 데이터 삭제
                cursor.execute(f"DELETE FROM {self.yaml_info}")
                
                # YAML 파일 읽기
                with open(self.config.YAML_PATH, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                
                # 데이터 파싱 및 삽입
                site_count = 0
                page_count = 0
                
                for site_name, site_info in data.items():
                    h_name = site_info.get('h_name', '')
                    base_url = site_info.get('url', '')
                    site_count += 1
                    
                    # pages 배열 처리
                    pages = site_info.get('pages', [])
                    for page in pages:
                        cursor.execute(f"""
                            INSERT INTO {self.yaml_info}
                            (site_name, page_id, h_name, "desc", url, detail_url)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            site_name,
                            page.get('id', ''),
                            h_name,
                            page.get('desc', ''),
                            base_url,
                            page.get('detail_url', '')
                        ))
                        page_count += 1
                        
                conn.commit()
                logger.info("YAML 데이터 로딩 완료")
                
                # 카운트 저장
                self._site_count = site_count
                self._page_count = page_count
                logger.info(f"사이트 수: {self._site_count}, 페이지 수: {self._page_count}")
                
                # 캐시 초기화 (다시 로드되도록)
                self._yaml_data_cache = None

        except Exception as e:
            logger.error(f"YAML 로딩 중 오류: {e}")
            if 'conn' in locals():
                conn.rollback()

    def load_yaml_data_to_dict(self, refresh_cache=False):
        """
        yaml_info 테이블의 모든 데이터를 dict 형태로 반환
        
        Args:
            refresh_cache (bool): True일 경우 캐시를 새로고침
            
        Returns:
            dict: {site_name: {page_id: {컬럼들...}, ...}, ...} 형태
        """
        if self._yaml_data_cache is not None and not refresh_cache:
            return self._yaml_data_cache
            
        try:
            with sqlite3.connect(self.summary_path) as conn:
                conn.row_factory = sqlite3.Row  # 컬럼명으로 접근 가능하도록
                cursor = conn.cursor()
                
                cursor.execute(f"""
                    SELECT site_name, page_id, h_name, "desc", url, detail_url
                    FROM {self.yaml_info}
                    ORDER BY site_name, page_id
                """)
                
                rows = cursor.fetchall()
                result = {}
                
                for row in rows:
                    site_name = row['site_name']
                    page_id = row['page_id']
                    
                    # site_name이 없으면 초기화
                    if site_name not in result:
                        result[site_name] = {}
                    
                    # 페이지 정보 저장
                    result[site_name][page_id] = {
                        'h_name': row['h_name'],
                        'desc': row['desc'],
                        'url': row['url'],
                        'detail_url': row['detail_url']
                    }
                
                # 캐시에 저장
                self._yaml_data_cache = result
                logger.info(f"YAML 데이터 dict 로딩 완료: 사이트 {len(result)}개")
                return result
                
        except Exception as e:
            logger.error(f"YAML 데이터 dict 로딩 중 오류: {e}")
            return {}

    def get_page_info(self, site_name, page_id):
        """
        특정 사이트의 특정 페이지 정보 반환
        
        Args:
            site_name (str): 사이트명
            page_id (str): 페이지 ID
            
        Returns:
            dict: 페이지 정보 또는 None
        """
        yaml_data = self.load_yaml_data_to_dict()
        return yaml_data.get(site_name, {}).get(page_id)

    def get_site_pages(self, site_name):
        """
        특정 사이트의 모든 페이지 정보 반환
        
        Args:
            site_name (str): 사이트명
            
        Returns:
            dict: 해당 사이트의 모든 페이지 정보
        """
        yaml_data = self.load_yaml_data_to_dict()
        return yaml_data.get(site_name, {})

    def get_all_sites(self):
        """
        모든 사이트명 리스트 반환
        
        Returns:
            list: 사이트명 리스트
        """
        yaml_data = self.load_yaml_data_to_dict()
        return list(yaml_data.keys())

    @property
    def site_count(self):
        """사이트 수 반환 (읽기 전용)"""
        if self._site_count is None:
            # DB에서 직접 계산
            try:
                with sqlite3.connect(self.summary_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT COUNT(DISTINCT site_name) FROM {self.yaml_info}")
                    self._site_count = cursor.fetchone()[0]
            except Exception as e:
                logger.error(f"사이트 수 조회 오류: {e}")
                return 0
        return self._site_count

    @property
    def page_count(self):
        """페이지 수 반환 (읽기 전용)"""
        if self._page_count is None:
            # DB에서 직접 계산
            try:
                with sqlite3.connect(self.summary_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT COUNT(*) FROM {self.yaml_info}")
                    self._page_count = cursor.fetchone()[0]
            except Exception as e:
                logger.error(f"페이지 수 조회 오류: {e}")
                return 0
        return self._page_count

    def refresh_counts(self):
        """사이트 수와 페이지 수를 다시 계산"""
        self._site_count = None
        self._page_count = None
        # property 접근으로 자동 계산됨
        return self.site_count, self.page_count
    
    def last_crawling_time(self):
        """
        마지막 크롤링 시간을 반환
        
        Returns:
            str: ISO 형식의 마지막 크롤링 시간
        """
        try:
            with sqlite3.connect(self.summary_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT upd_time FROM law_summary order by upd_time desc LIMIT 1")
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"마지막 크롤링 시간 조회 오류: {e}")
            return None