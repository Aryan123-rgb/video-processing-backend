import logging
from services.queue import get_rabbitmq_connection, callback
from services.redis_client import get_redis_client
from services.storage import get_mongodb_connection
from config import settings
import time 

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    while True:
        try:
            logger.info("Connecting to redis...")
            redis_client = get_redis_client()
            redis_client.ping()
            
            logger.info("Connecting to Mongodb database...")
            db = get_mongodb_connection()
            
            logger.info("Connecting with rabbitmq...")
            connection = get_rabbitmq_connection()
            channel = connection.channel()
            
            channel.queue_declare(queue=settings.rabbitmq_whisper_queue, durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(
                queue=settings.rabbitmq_whisper_queue,
                on_message_callback=callback
            )
            
            logger.info("Worker active, waiting for the message...")
            
            channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Worker shutting down...")
            break
        
        except Exception as e:
            logger.error(f"Failed to connect with services {str(e)}")
            logger.info(f"Retrying in 5 seconds...")
            time.sleep(5)
            
if __name__ == "__main__":
    main()