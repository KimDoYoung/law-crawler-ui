"""
대시보드 API 엔드포인트
"""

import os
import re
from pathlib import Path
from fastapi import APIRouter, Query
from app.backend.page_contexts.dashboard_context import (
    get_dashboard_metrics,
    get_dashboard_data,
)
from app.backend.data.db_util import attach_list
from app.backend.core.logger import get_logger
from app.backend.core.config import config

logger = get_logger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/metrics", response_model=dict)
async def get_metrics():
    """
    대시보드 메트릭 데이터 조회 (주요 통계)

    Returns:
        - site_count: 수집 사이트 수
        - today_collect: 오늘 수집 데이터
        - three_days_collect: 3일 수집 데이터
        - seven_days_collect: 7일 수집 데이터
        - total_collect: 전체 수집 데이터
        - error_count: 오류 발생 건수
    """
    try:
        metrics = get_dashboard_metrics()
        return metrics
    except Exception as e:
        logger.error(f"❌ 대시보드 메트릭 조회 실패: {e}")
        return {
            "site_count": "-",
            "today_collect": "-",
            "three_days_collect": "-",
            "seven_days_collect": "-",
            "total_collect": "-",
            "error_count": 0,
        }


@router.get("/data", response_model=list)
async def get_data(
    period: str = Query("today", description="기간: today, 3days, 7days"),
):
    """
    대시보드 테이블 데이터 조회

    Args:
        period: 'today' (기본값), '3days', '7days'

    Returns:
        테이블 행 리스트
    """
    try:
        data = get_dashboard_data(period)
        return data
    except Exception as e:
        logger.error(f"❌ 대시보드 데이터 조회 실패: {e}")
        return []


@router.get("/crawler-health", response_model=dict)
async def get_crawler_health():
    """
    크롤러 헬스 체크

    Returns:
        - healthy: 'ok' (정상) 또는 'check' (오류 발생)
        - last_crawling_time: 마지막 크롤링 시간
        - error_message: 오류 메시지 (있는 경우만)
    """
    try:
        if not config.CRAWLER_LOG_DIR:
            return {
                "healthy": "check",
                "last_crawling_time": None,
                "error_message": "로그 디렉토리가 설정되지 않았습니다."
            }

        log_dir = Path(config.CRAWLER_LOG_DIR)
        if not log_dir.exists():
            return {
                "healthy": "check",
                "last_crawling_time": None,
                "error_message": "로그 디렉토리를 찾을 수 없습니다."
            }

        # 가장 최근 로그 파일 찾기 (law_crawler_*.log 패턴)
        log_files = sorted(
            log_dir.glob("law_crawler_*.log"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )

        if not log_files:
            return {
                "healthy": "check",
                "last_crawling_time": None,
                "error_message": "로그 파일을 찾을 수 없습니다."
            }

        latest_log = log_files[0]
        logger.info(f"최근 로그 파일: {latest_log}")

        # 로그 파일 읽기
        has_error = False
        last_timestamp = None

        try:
            with open(latest_log, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

                # 마지막 라인의 시각 추출
                for line in reversed(lines):
                    if line.strip():
                        # 로그 형식: [시간] [로그레벨] 메시지
                        # 예: 2025-01-30 10:30:45,123 - INFO - message
                        match = re.match(r'(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})', line)
                        if match:
                            last_timestamp = match.group(1)
                            break

                # ERROR 검색
                for line in lines:
                    if 'ERROR' in line or 'Exception' in line:
                        has_error = True
                        break

        except Exception as e:
            logger.error(f"로그 파일 읽기 실패: {e}")
            return {
                "healthy": "check",
                "last_crawling_time": None,
                "error_message": f"로그 파일 읽기 실패: {str(e)}"
            }

        return {
            "healthy": "check" if has_error else "ok",
            "last_crawling_time": last_timestamp,
            "error_detected": has_error
        }

    except Exception as e:
        logger.error(f"크롤러 헬스 체크 실패: {e}")
        return {
            "healthy": "check",
            "last_crawling_time": None,
            "error_message": f"헬스 체크 실패: {str(e)}"
        }


@router.get("/attachments/{site_code}/{page_code}/{real_seq}")
async def get_attachments(site_code: str, page_code: str, real_seq: str):
    """
    특정 항목의 첨부파일 목록 조회

    Args:
        site_code: 사이트 코드
        page_code: 페이지 코드
        real_seq: 시퀀스 번호

    Returns:
        첨부파일 목록
    """
    try:
        attach_df = attach_list(site_code, page_code, real_seq)
        attachments_data = []

        for _, attach_row in attach_df.iterrows():
            save_file_name = attach_row.get("save_file_name", "")
            save_folder = attach_row.get("save_folder", "")
            attach_url = f"/api/v1/attachments/{save_folder}/{save_file_name}"

            attachments_data.append({
                "name": save_file_name,
                "url": attach_url
            })

        return {
            "count": len(attachments_data),
            "items": attachments_data
        }
    except Exception as e:
        logger.error(f"❌ 첨부파일 조회 실패 ({site_code}/{page_code}/{real_seq}): {e}")
        return {
            "count": 0,
            "items": []
        }
