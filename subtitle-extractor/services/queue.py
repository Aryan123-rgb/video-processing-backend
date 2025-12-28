import pika
import logging
from config import settings
import json
from utils.extract_subtitle import extract_subtitle
from services.redis_client import update_job_status, JobStatus
from services.storage import mongodb

logger = logging.getLogger(__name__)

def get_rabbmitmq_connection_channel():
    credentials = pika.PlainCredentials(
        username=settings.rabbitmq_user,
        password=settings.rabbitmq_pass
    )
    parameters = pika.ConnectionParameters(
        host=settings.rabbitmq_host,
        port=settings.rabbitmq_port,
        credentials=credentials
    )
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    return channel

class Queue:
    def __init__(self):
        self.channel = get_rabbmitmq_connection_channel()
        self.channel.queue_declare(queue=settings.rabbitmq_ffmpeg_extractor_queue, durable=True)
        self.channel.queue_declare(queue=settings.rabbitmq_whisper_queue, durable=True)
    
    def publish_transcription_task(self, video_id: str, video_path: str):
        message = {
            "video_id": video_id,
            "video_path": video_path
        }
        
        self.channel.basic_publish(
            exchange="",
            routing_key=settings.rabbitmq_whisper_queue,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent
            )
        )
        logger.info(f"Message published for whisper worker with video_id {video_id}")
    
    def callback(self, ch, method, properties, body):
        try:
            message = json.loads(body)
            video_id = message['video_id']
            video_path = message['video_path']
            
            logger.info(f"Processing video {video_id}")
            
            # Update the job status to processing
            update_job_status(video_id, JobStatus.PROCESSING)
            
            # Process the video -> Extract subtitles
            subtitle = extract_subtitle(video_id, video_path)
            
            # Save the subtitle to mongodb
            mongodb.save_subtitles(video_id, subtitle)
            
            if subtitle:
                # Update the job status to complete
                update_job_status(video_id, JobStatus.COMPLETED)
                logger.info(f"Video {video_id} processing complete")
            else:
                self.publish_transcription_task(video_id, video_path)
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Failed to process video: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
queue = Queue()
        


        
        
