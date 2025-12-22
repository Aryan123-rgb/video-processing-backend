from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from services.storage import storage_service
from services.queue import queue_service
from services.redis_client import JobStatus, create_job, get_job_data
from config import settings
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/video/upload")
async def upload_video(file: UploadFile = File(...)):
    if not file.filename or not file:
        raise HTTPException(
            status_code=400,
            detail="Invalid file provided"
        )
    
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in settings.allowed_extension:
        raise HTTPException(
            status_code=400,
            detail="Invalid file provided"
        )
        
    file.file.seek(0)
    
    try:
        # Upload the video to the storage
        video_id, video_path = storage_service.save_video(file.file, file.filename)
        logger.info("Video uploaded successfully")
        
        # Create an entry in the redis db
        create_job(video_id, file.filename)
        logger.info("Job created in redis")

        # publish a message to the message queue
        queue_service.publish_video_task(video_id, video_path)
        logger.info(f"Message Published to the queue with {video_id}")        
        
        return {
            "video_id": video_id,
            "filename": file.filename,
            "status": JobStatus.PENDING,
            "message": "Video successfully uploaded."
        }
        
    except Exception as e:
        logger.error(f"Upload failed {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to upload video"
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