import logging 
import time
from services.queue import get_rabbmitmq_connection, callback
from services.redis_client import get_redis_client
from config import settings 

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    while True:
        try:
            logger.info("Connecting to redis client....")
            redis_client = get_redis_client()
            
            logger.info("Connecting to RabbitMQ...")
            connection = get_rabbmitmq_connection()
            channel = connection.channel()
            
            channel.queue_declare(queue=settings.rabbitmq_queue, durable=True)
            
            channel.basic_qos(prefetch_count=1)
            
            channel.basic_consume(
                queue=settings.rabbitmq_queue,
                on_message_callback=callback
            )
            
            logger.info("Worker started. Listening for messages...")
            
            channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("Worker shutting down...")
            break
        
        except Exception as e:
            logger.error(f"Failed to connect with RabbitMQ...{str(e)}")
            logger.info("Retrying in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    main()    
