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
    
def create_job(video_id: str, filename: str):
    job = {
        "video_id": video_id,
        "filename": filename,
        "status": JobStatus.PENDING,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    redis_client.set(video_id, json.dumps(job))
    return job

def update_job_status(video_id: str, status: str):
    job = redis_client.get(video_id)
    if job:
        job['status'] = status

def get_job_data(video_id: str):
    job = redis_client.get(video_id)
    return json.loads(job) if job else None

        
def delete_job(video_id: str):
    redis_client.delete(video_id)
    