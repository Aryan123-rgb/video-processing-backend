import pika
from config import settings
import logging
import json 

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
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    return channel

class Queue:
    def __init__(self):
        self.channel = get_rabbitmq_connection()
        self.channel.queue_declare(queue=settings.rabbitmq_ffmpeg_extractor_queue, durable=True)
        
    def publish_extraction_task(self, video_id: str, video_path: str):
        message = {
            "video_id": video_id,
            "video_path": video_path
        }
        
        self.channel.basic_publish(
            exchange="",
            routing_key=settings.rabbitmq_ffmpeg_extractor_queue,
            body=json.dumps(message)
        )
        logger.info("Message Published to the ffmpeg extractor queue...")
        
queue = Queue()