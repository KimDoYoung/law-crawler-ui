"""
첨부파일 다운로드 API 엔드포인트
"""
from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import FileResponse
from pathlib import Path as PathlibPath
from app.backend.core.config import config
from app.backend.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/attachments", tags=["attachments"])


@router.get("/{save_folder:path}/{filename}")
async def download_attachment(save_folder: str = Path(...), filename: str = Path(...)):
    """
    첨부파일 다운로드

    Args:
        save_folder: 저장 폴더 경로 (예: kofia/menu_4)
        filename: 파일명

    Returns:
        FileResponse: 첨부파일
    """
    try:
        # 첨부파일 경로 구성
        # LAW_CRAWLER_DIR/Attaches/{save_folder}/{filename}
        attach_base = PathlibPath(config.ATTACHS_DIR)
        file_path = attach_base / save_folder / filename

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
