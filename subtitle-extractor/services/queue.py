import pika
import logging
from config import settings
import json
from utils.extract_subtitle import extract_subtitle
from services.redis_client import update_job_status, JobStatus

logger = logging.getLogger(__name__)

def get_rabbmitmq_connection():
    credentials = pika.PlainCredentials(
        username=settings.rabbitmq_user,
        password=settings.rabbitmq_pass
    )
    parameters = pika.ConnectionParameters(
        host=settings.rabbitmq_host,
        port=settings.rabbitmq_port,
        credentials=credentials
    )
    return pika.BlockingConnection(parameters)

def callback(ch, method, properties, body):
    try:
        message = json.loads(body)
        video_id = message['video_id']
        video_path = message['video_path']
        
        logger.info(f"Processing video {video_id}")
        
        # Update the job status to processing
        update_job_status(video_id, JobStatus.PROCESSING)
        
        # Process the video -> Extract subtitles
        extract_subtitle(video_id, video_path)
        
        # Update the job status to complete
        update_job_status(video_id, JobStatus.COMPLETED)

        logger.info(f"Video {video_id} processing complete")
        
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Failed to process video: {str(e)}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        
