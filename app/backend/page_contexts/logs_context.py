"""
로그 관리 페이지 컨텍스트 제공 함수
"""

from datetime import datetime, timedelta
from app.backend.data.log_util import get_log_data
from app.backend.core.logger import get_logger
import os
import glob

logger = get_logger(__name__)


def get_available_dates(days_back=7):
    """
    사용 가능한 로그 날짜 목록 반환

    Args:
        days_back: 과거 며칠의 날짜를 보여줄지

    Returns:
        [{"date": "2025-01-01", "label": "2025-01-01"}, ...]
    """
    dates = []
    for i in range(days_back):
        date = datetime.now() - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        dates.append({"date": date_str, "label": date_str})
    return dates


def get_crawler_log(log_date: str):
    """
    크롤러 로그 내용 반환

    Args:
        log_date: 로그 날짜 (YYYY-MM-DD)

    Returns:
        {"content": "로그 내용", "path": "파일경로", "filename": "파일명"}
    """
    try:
        # log_date 형식: YYYY-MM-DD
        date_obj = datetime.strptime(log_date, "%Y-%m-%d").date()
        log_content, log_fullpath = get_log_data(date_obj)

        if log_content is None or len(log_content) == 0:
            return {
                "content": "해당 날짜의 로그가 없습니다.",
                "path": "",
                "filename": "",
            }

        content_text = "\n".join(line.rstrip("\n") for line in log_content)
        filename = log_fullpath.split("\\")[-1] if log_fullpath else "log.txt"

        return {"content": content_text, "path": log_fullpath, "filename": filename}
    except Exception as e:
        logger.error(f"❌ 크롤러 로그 로드 실패: {e}")
        return {"content": f"로그 로드 중 오류 발생: {e}", "path": "", "filename": ""}


def get_ui_log():
    """
    FastAPI UI 로그 내용 반환

    Returns:
        {"content": "로그 내용", "path": "파일경로", "filename": "파일명"}
    """
    try:
        from app.backend.core.config import config

        log_file = os.path.join(config.UI_LOG_DIR, "law_crawler.log")

        if not os.path.exists(log_file):
            return {"content": "UI 로그가 없습니다.", "path": "", "filename": ""}

        with open(log_file, "r", encoding="utf-8") as f:
            log_lines = f.readlines()

        if not log_lines:
            return {"content": "UI 로그가 없습니다.", "path": "", "filename": ""}

        content_text = "\n".join(line.rstrip("\n") for line in log_lines)
        filename = log_file.split("\\")[-1] if log_file else "ui.log"

        return {"content": content_text, "path": log_file, "filename": filename}
    except Exception as e:
        logger.error(f"❌ UI 로그 로드 실패: {e}")
        return {"content": f"로그 로드 중 오류 발생: {e}", "path": "", "filename": ""}


def get_crawler_log_files():
    """
    크롤러 로그 파일 목록 반환 (최신 날짜 우선 정렬)

    Returns:
        [{"filename": "law_crawler_2025-10-23.log", "path": "전체경로", "modified_time": "2025-10-23 10:00:00"}, ...]
    """
    try:
        from app.backend.core.config import config

        log_dir = config.CRAWLER_LOG_DIR
        if not os.path.exists(log_dir):
            logger.warning(f"⚠️ 크롤러 로그 디렉터리가 존재하지 않습니다: {log_dir}")
            return []

        # *.log 파일 찾기
        log_pattern = os.path.join(log_dir, "*.log")
        log_files = glob.glob(log_pattern)

        if not log_files:
            return []

        # 파일 정보 수집
        file_list = []
        for file_path in log_files:
            try:
                # 파일 수정 시간 가져오기
                modified_time = os.path.getmtime(file_path)
                modified_datetime = datetime.fromtimestamp(modified_time)

                filename = os.path.basename(file_path)
                file_list.append({
                    "filename": filename,
                    "path": file_path,
                    "modified_time": modified_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                    "modified_timestamp": modified_time  # 정렬용
                })
            except Exception as e:
                logger.warning(f"⚠️ 파일 정보 읽기 실패 ({file_path}): {e}")
                continue

        # 최신 날짜 우선 정렬 (수정 시간 기준 내림차순)
        file_list.sort(key=lambda x: x["modified_timestamp"], reverse=True)

        # 정렬용 timestamp 제거
        for file_info in file_list:
            del file_info["modified_timestamp"]

        return file_list
    except Exception as e:
        logger.error(f"❌ 크롤러 로그 파일 목록 조회 실패: {e}")
        return []


def get_crawler_log_by_filename(filename: str):
    """
    크롤러 로그 파일 내용 반환

    Args:
        filename: 로그 파일명

    Returns:
        {"content": "로그 내용", "path": "파일경로", "filename": "파일명"}
    """
    try:
        from app.backend.core.config import config

        log_file = os.path.join(config.CRAWLER_LOG_DIR, filename)

        if not os.path.exists(log_file):
            return {"content": "해당 로그 파일이 없습니다.", "path": "", "filename": ""}

        with open(log_file, "r", encoding="utf-8") as f:
            log_lines = f.readlines()

        if not log_lines:
            return {"content": "로그 내용이 없습니다.", "path": log_file, "filename": filename}

        content_text = "\n".join(line.rstrip("\n") for line in log_lines)

        return {"content": content_text, "path": log_file, "filename": filename}
    except Exception as e:
        logger.error(f"❌ 크롤러 로그 파일 조회 실패: {e}")
        return {"content": f"로그 조회 중 오류 발생: {e}", "path": "", "filename": ""}
