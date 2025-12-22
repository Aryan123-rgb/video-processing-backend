import pika
import json
import logging
from config import settings

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

class QueueService:
    def __init__(self):
        self.connection = get_rabbitmq_connection()
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=settings.rabbitmq_queue, durable=True)
        
    def publish_video_task(self, video_id: str, video_path: str):
        message = {
            "video_id": video_id,
            "video_path": video_path 
        }
        
        self.channel.basic_publish(
            exchange="",
            routing_key=settings.rabbitmq_queue,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2
            )
        )
        logger.info(f"Published task for video {video_id}")
        
    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()

queue_service = QueueService()