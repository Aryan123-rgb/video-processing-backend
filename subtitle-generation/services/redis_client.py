from redis import Redis
import json
import logging
from config import settings
from datetime import datetime

logger = logging.getLogger(__name__)

def get_redis_client():
    return Redis(
        port=settings.redis_port,
        host=settings.redis_host,
        db=settings.redis_db         
    )

redis_client = get_redis_client()

def get_job_data(video_id: str):
    job_data = redis_client.get(video_id)
    return json.loads(job_data) if job_data else None

def update_job_status(video_id: str, status: str):
    job_data = get_job_data(video_id)
    if job_data:
        job_data['status'] = status
        job_data['updated_at'] = datetime.now().isoformat()
        redis_client.set(video_id, json.dumps(job_data))
    else:
        logger.warning(f"Job with video id {video_id} not found")
        return None