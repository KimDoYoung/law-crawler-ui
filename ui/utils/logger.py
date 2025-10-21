# utils/logger.py
"""
모듈 설명: 
    - streamlit ui logger
주요 기능:
    - logger = setup_logger()
    - logger.info("정보 메시지")
    - app.py 하위에 .logs에 law-crawler-ui.log 파일 생성
    - 5MB 크기 제한
작성자: 김도영
작성일: 2025-06-02
버전: 1.0
"""

from collections import deque
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name: str = 'law-ui-logger', log_dir: str = 'logs', level=logging.INFO):
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'law-crawler-ui.log')

    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger

    logger.setLevel(level)

    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding='utf-8'
    )
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 콘솔 출력 (선택 사항)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger

def get_logger_filepath(logger: logging.Logger) -> str:
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            return handler.baseFilename
    return None

def get_ui_log_contents(logger: logging.Logger, max_lines: int = 500):
    log_file_path = get_logger_filepath(logger)
    if not log_file_path or not os.path.exists(log_file_path):
        return [], log_file_path

    with open(log_file_path, 'r', encoding='utf-8') as file:
        last_lines = deque(file, maxlen=max_lines)

    return list(last_lines), log_file_path

# def get_ui_log_contents(logger: logging.Logger):
#     """
#     로거의 로그 파일 내용을 문자열배열과 로그파일path를 리턴
    
#     Args:
#         logger (logging.Logger): 로그를 기록하는 로거 객체
    
#     Returns:
#         tuple: (로그 내용의 문자열 배열, 로그 파일 경로)
#     """
#     log_file_path = get_logger_filepath(logger)
#     if not log_file_path or not os.path.exists(log_file_path):
#         return [], log_file_path

#     with open(log_file_path, 'r', encoding='utf-8') as file:
#         log_contents = file.readlines()
    
#     return log_contents, log_file_path