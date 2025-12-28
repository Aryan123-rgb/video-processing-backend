import pika 
from config import settings
import logging
import json
from services.redis_client import update_job_status
from utils.whisper_subtitle_generation import generate_subtitle
from services.storage import mongodb

logger = logging.getLogger(__name__)

def get_rabbitmq_connection():
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
        
        logger.info(f"Extracting subtitle for {video_id}")
                
        # Extract the subtitle from video using whisper
        subtitle = generate_subtitle(video_path)
        
        # save the subtitle file or contents to mongodb
        mongodb.save_subtitles(video_id, subtitle_content=subtitle)
        
        # Update the entry into the redis db -> Mark the video_processing complete in the redis database
        update_job_status(video_id, "COMPLETED")
        
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        logger.error(f"Video subtitle generation failed due to {str(e)}")  
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)