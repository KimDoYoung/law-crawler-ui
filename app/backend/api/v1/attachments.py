"""
첨부파일 다운로드 API 엔드포인트
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from app.backend.core.config import config
from app.backend.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/attachments", tags=["attachments"])


@router.get("/{site_code}/{page_code}/{real_seq}/{filename}")
async def download_attachment(site_code: str, page_code: str, real_seq: str, filename: str):
    """
    첨부파일 다운로드

    Args:
        site_code: 사이트 코드
        page_code: 페이지 코드
        real_seq: 시퀀스 번호
        filename: 파일명

    Returns:
        FileResponse: 첨부파일
    """
    try:
        # 첨부파일 경로 구성
        # LAW_CRAWLER_DIR/Attaches/{site_code}/{page_code}_{real_seq}/{filename}
        attach_base = Path(config.ATTACHS_DIR)
        file_path = attach_base / site_code / f"{page_code}_{real_seq}" / filename

        logger.info(f"첨부파일 다운로드 요청: {file_path}")

        if not file_path.exists():
            logger.error(f"❌ 첨부파일을 찾을 수 없습니다: {file_path}")
            raise HTTPException(status_code=404, detail="첨부파일을 찾을 수 없습니다")

        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/octet-stream"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 첨부파일 다운로드 실패: {e}")
        raise HTTPException(status_code=500, detail="첨부파일 다운로드 중 오류가 발생했습니다")
