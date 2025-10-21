
import os
import sys
import psutil

REQUIRED_ENV_VARS = ["LAW_CRAWLER_EXE_DIR"]
REQUIRED_FILES = ["LAW_SITE_DESC.yaml", ".env"]

def validate_environment():
    """ 
        ui가 돌 수 있는 환경인지 체크
        1. 환경변수 LAW_CRAWLER_EXE_DIR=c:\law_crawler\exe 와 같이 설정되어 있어야함
        2. 1.의 폴더에 .env가 존재해야함.
        2. 1.의 폴도에 LAW_SITE_DESC.yaml 파일이 존재해야함
    """
    for var in REQUIRED_ENV_VARS:
        if os.getenv(var) is None:
            print(f"❌ 환경변수 {var}가 설정되어 있지 않습니다.")
            sys.exit(1)
    exe_dir = os.getenv("LAW_CRAWLER_EXE_DIR")
    if not exe_dir or not os.path.isdir(exe_dir):
        print(f"❌ 환경변수 LAW_CRAWLER_EXE_DIR={exe_dir}가 유효한 디렉토리가 아닙니다.")
        sys.exit(1)
         
    # 필수 파일 존재 확인
    for filepath in REQUIRED_FILES:
        filepath = os.path.join(exe_dir, filepath)
         # exe_dir 하위에 파일이 존재하는지 확인
         # .env 파일과 LAW_SITE_DESC.yaml 파일이 존재해야함
         # .env 파일은 환경변수 설정을 위해 필요하고, LAW_SITE_DESC.yaml은 사이트 정보 정의를 위해 필요함
        if not os.path.exists(filepath):
            print(f"❌ 필수 파일이 없습니다: {filepath}")
            sys.exit(1)

def crawler_status():
    """
    Check if the crawler is running by looking for the 'crawler' process.
    Returns True if the crawler is running, False otherwise.
    """

    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'crawler':
            return True
    return False