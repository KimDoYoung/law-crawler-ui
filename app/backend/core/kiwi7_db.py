import sqlite3
import os
from backend.core.logger import get_logger

logger = get_logger(__name__)

def create_kiwi7_db(db_path: str):
    """
    키위7 데이터베이스를 생성하는 함수
    sql/kiwi7_ddl.sql 파일을 읽어서 DDL 스크립트를 실행합니다.
    
    Args:
        db_path (str): 데이터베이스 파일 경로
        
    Returns:
        bool: 데이터베이스 생성 성공 여부
        
    Raises:
        DatabaseCreationError: 데이터베이스 생성 실패 시
    """
    ddl_file_path = 'sqls/kiwi7_ddl.sql'
    conn = None
    
    try:
        # DDL 파일 존재 여부 확인
        if not os.path.exists(ddl_file_path):
            raise FileNotFoundError(f"DDL 파일을 찾을 수 없습니다: {ddl_file_path}")
        
        # 데이터베이스 디렉토리 생성
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            logger.info(f"데이터베이스 디렉토리 생성: {db_dir}")
        
        # DDL 파일 읽기
        logger.info(f"DDL 파일 읽기 시작: {ddl_file_path}")
        with open(ddl_file_path, 'r', encoding='utf-8') as f:
            ddl_sql = f.read()
        
        # DDL 스크립트가 비어있는지 확인
        if not ddl_sql.strip():
            raise ValueError("DDL 파일이 비어있습니다.")
        
        # 데이터베이스 연결
        logger.info(f"데이터베이스 연결 시작: {db_path}")
        conn = sqlite3.connect(db_path)
        
        # 연결 상태 확인
        conn.execute("SELECT 1")
        
        cursor = conn.cursor()
        
        # DDL 스크립트 실행
        logger.info("DDL 스크립트 실행 시작")
        cursor.executescript(ddl_sql)
        
        # 변경사항 커밋
        conn.commit()
        
        # 생성된 테이블 목록 확인
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        logger.info(f"생성된 테이블: {table_names}")
        
        logger.info(f"데이터베이스 생성 완료: {db_path}")
        return True
        
    except FileNotFoundError as e:
        # DDL 파일을 찾을 수 없는 경우
        logger.error(f"DDL 파일 오류: {str(e)}")
        raise DatabaseCreationError(f"DDL 파일 오류: {str(e)}") from e
        
    except sqlite3.Error as e:
        # SQLite 관련 오류
        logger.error(f"SQLite 데이터베이스 오류: {str(e)}")
        
        # 손상된 데이터베이스 파일 삭제 시도
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
                logger.info(f"손상된 데이터베이스 파일 삭제: {db_path}")
            except OSError as delete_error:
                logger.warning(f"데이터베이스 파일 삭제 실패: {delete_error}")
        
        raise DatabaseCreationError(f"데이터베이스 생성 오류: {str(e)}") from e
        
    except (IOError, OSError) as e:
        # 파일 입출력 오류
        logger.error(f"파일 시스템 오류: {str(e)}")
        raise DatabaseCreationError(f"파일 시스템 오류: {str(e)}") from e
        
    except ValueError as e:
        # DDL 내용 관련 오류
        logger.error(f"DDL 내용 오류: {str(e)}")
        raise DatabaseCreationError(f"DDL 내용 오류: {str(e)}") from e
        
    except Exception as e:
        # 예상치 못한 오류
        logger.error(f"예상치 못한 오류 발생: {str(e)}", exc_info=True)
        raise DatabaseCreationError(f"데이터베이스 생성 중 예상치 못한 오류: {str(e)}") from e
        
    finally:
        # 데이터베이스 연결 종료
        if conn:
            try:
                conn.close()
                logger.debug("데이터베이스 연결 종료")
            except Exception as close_error:
                logger.warning(f"데이터베이스 연결 종료 중 오류: {close_error}")


def create_kiwi7_db_with_retry(db_path: str, max_retries: int = 3) -> bool:
    """
    재시도 로직이 포함된 데이터베이스 생성 함수
    
    Args:
        db_path (str): 데이터베이스 파일 경로
        max_retries (int): 최대 재시도 횟수 (기본값: 3)
        
    Returns:
        bool: 데이터베이스 생성 성공 여부
    """
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"데이터베이스 생성 시도 {attempt}/{max_retries}")
            result = create_kiwi7_db(db_path)
            
            if result:
                logger.info(f"데이터베이스 생성 성공 (시도: {attempt})")
                return True
                
        except DatabaseCreationError as e:
            logger.warning(f"데이터베이스 생성 실패 (시도 {attempt}/{max_retries}): {str(e)}")
            
            if attempt == max_retries:
                logger.error(f"모든 재시도 실패. 데이터베이스 생성 포기: {db_path}")
                raise e
            
            # 다음 시도 전 대기 (점진적 백오프)
            import time
            wait_time = attempt * 1.0  # 1초, 2초, 3초...
            logger.info(f"{wait_time}초 대기 후 재시도...")
            time.sleep(wait_time)
    
    return False


def validate_database(db_path: str) -> bool:
    """
    생성된 데이터베이스의 유효성을 검증하는 함수
    
    Args:
        db_path (str): 검증할 데이터베이스 파일 경로
        
    Returns:
        bool: 데이터베이스 유효성 검증 결과
    """
    try:
        if not os.path.exists(db_path):
            logger.error(f"데이터베이스 파일이 존재하지 않음: {db_path}")
            return False
        
        # 데이터베이스 연결 테스트
        conn = sqlite3.connect(db_path)
        
        # 기본 쿼리 실행 테스트
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()
        logger.info(f"SQLite 버전: {version[0]}")
        
        # 테이블 존재 여부 확인
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        
        if table_count == 0:
            logger.warning("생성된 테이블이 없습니다.")
            return False
        
        logger.info(f"데이터베이스 검증 완료: {table_count}개 테이블 존재")
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"데이터베이스 검증 실패: {str(e)}")
        return False


class DatabaseCreationError(Exception):
    """
    데이터베이스 생성 관련 커스텀 예외 클래스
    """
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


# 사용 예시 및 테스트 함수
def initialize_kiwi7_database(db_path: str = "data/kiwi7.db"):
    """
    키위7 데이터베이스 초기화 메인 함수
    
    Args:
        db_path (str): 데이터베이스 파일 경로
    """
    try:
        logger.info("키위7 데이터베이스 초기화 시작")
        
        # 재시도를 포함한 데이터베이스 생성
        success = create_kiwi7_db_with_retry(db_path)
        
        if success:
            # 데이터베이스 검증
            if validate_database(db_path):
                logger.info("키위7 데이터베이스 초기화 완료")
            else:
                raise DatabaseCreationError("데이터베이스 검증 실패")
        else:
            raise DatabaseCreationError("데이터베이스 생성 실패")
            
    except Exception as e:
        logger.error(f"데이터베이스 초기화 실패: {str(e)}")
        # 실패한 경우 기본 테이블만이라도 생성하는 폴백 로직
        create_minimal_database(db_path)
        

def create_minimal_database(db_path: str):
    """
    최소한의 기본 테이블만 생성하는 폴백 함수
    
    Args:
        db_path (str): 데이터베이스 파일 경로
    """
    try:
        logger.info("최소한의 기본 데이터베이스 생성 시도")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 기본 설정 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                name TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 기본 설정 데이터 삽입
        cursor.execute('INSERT OR IGNORE INTO settings (name, value) VALUES (?, ?)', 
                      ('user_id', 'kdy987'))
        cursor.execute('INSERT OR IGNORE INTO settings (name, value) VALUES (?, ?)', 
                      ('user_pw', '1111'))
        
        conn.commit()
        conn.close()
        
        logger.info("기본 데이터베이스 생성 완료")
        
    except Exception as e:
        logger.error(f"기본 데이터베이스 생성도 실패: {str(e)}")
        raise DatabaseCreationError(f"모든 데이터베이스 생성 시도 실패: {str(e)}")