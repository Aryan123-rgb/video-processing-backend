from redis import Redis 
import json
from config import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

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

def update_job_status(video_id: str, status: str):
    job_data = get_job_data(video_id)
    if job_data:
        job_data['status'] = status
        job_data['updated_at'] = datetime.now().isoformat()
        redis_client.set(video_id, json.dumps(job_data))
    else:
        logger.warning(f"Job with {video_id} not found")

def get_job_data(video_id: str):
    job = redis_client.get(video_id)
    return json.loads(job) if job else None

        
def delete_job(video_id: str):
    redis_client.delete(video_id)
    