from redis import Redis 
import json
from config import settings
from typing import Optional
from datetime import datetime

def get_redis_client():
    return Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        decode_responses=True
    )

redis_client = get_redis_client()

class JobStatus:
    PENDING = "pending"
    COMPLETED = "completed"
    PROCESSING = "processing"
    FAILED = "failed"

def create_job_with_outbox(
    video_id: str,
    filename: str,
    video_path: str
):
    message = {
        "video_id": video_id,
        "filename": filename,
        "video_path": video_path,
        "updated_at": datetime.now().isoformat(),
        "created_at": datetime.now().isoformat(),
        "status": JobStatus.PENDING,
    }
    with redis_client.pipeline(transaction=True) as pipe:
        pipe.set(
            video_id,
            json.dumps(message)
        )
        
        pipe.xadd(
            "outbox:video_jobs",
            {
                "event_type": "VIDEO_UPLOADED",
                "video_id": video_id,
                "filename": filename,
                "video_path": video_path,
                "created_at": datetime.now().isoformat()
            }
        )
        pipe.execute()

def update_job_status(video_id: str, status: str):
    job_data = get_job_data(video_id)
    if job_data:
        job_data['status'] = status
        job_data['updated_at'] = datetime.now().isoformat()
        redis_client.set(video_id, json.dumps(job_data))

def get_job_data(video_id: str):
    job = redis_client.get(video_id)
    return json.loads(job) if job else None

        
def delete_job(video_id: str):
    redis_client.delete(video_id)
    