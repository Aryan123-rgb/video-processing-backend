from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from services.storage import storage_service
from services.queue import queue_service
from services.redis_client import JobStatus, create_job_with_outbox, get_job_data
from config import settings
from pathlib import Path
import logging
# import magic
from io import BytesIO

logger = logging.getLogger(__name__)

router = APIRouter()

# def is_video(file_bytes: bytes) -> bool:
#     mime = magic.from_buffer(file_bytes, mime=True)
#     return mime.startswith("video/")    

@router.post("/video/upload")
async def upload_video(file: UploadFile = File(...)):
    # Check for null file or corrupt file
    if not file.filename or not file:
        raise HTTPException(
            status_code=400,
            detail="Invalid file provided"
        )
    
    file_ext = Path(file.filename).suffix.lower()
    
    # Check whether the video is provided or not
    # if file_ext not in settings.allowed_extension or not is_video(file.file):
    #     raise HTTPException(
    #         status_code=400,
    #         detail="Invalid file provided"
    #     )
        
    file.file.seek(0)
    
    try:
        # Upload the video to the storage
        video_id, video_path = storage_service.save_video(file.file, file.filename)
        logger.info("Video uploaded successfully")
        
        # Create an entry in the redis db
        create_job_with_outbox(video_id, file.filename, video_path)
        logger.info("Job created in redis")       
        
        return {
            "video_id": video_id,
            "video_path": video_path,
            "filename": file.filename,
            "status": JobStatus.PENDING,
            "message": "Video successfully uploaded."
        }
        
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/video/{video_id}/status")
async def get_video_status(video_id: str):
    job = get_job_data(video_id)
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail="Video not found"
        )
    return job

@router.get("/download/subtitle/{video_id}")
async def download_subtitle(video_id: str):
    subtitle_doc = storage_service.get_subtitles(video_id)

    if not subtitle_doc or "subtitle" not in subtitle_doc:
        raise HTTPException(status_code=404, detail="Subtitle not found")

    subtitle_text = subtitle_doc["subtitle"]

    file_like = BytesIO(subtitle_text.encode("utf-8"))

    headers = {
        "Content-Disposition": f'attachment; filename="{video_id}.srt"'
    }

    return StreamingResponse(
        file_like,
        media_type="application/x-subrip",
        headers=headers
    )
