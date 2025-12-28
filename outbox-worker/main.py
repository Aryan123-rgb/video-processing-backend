from services.queue import get_rabbitmq_connection
from services.redis_client import RedisClient
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    while True:
        try:
            logger.info("Connecting to Redis...")
            redis_client = RedisClient()
            
            logger.info("Connecting to rabbitmq...")
            channel = get_rabbitmq_connection()
            
            logger.info("Starting outbox worker...")
            redis_client.outbox_worker()
        except KeyboardInterrupt:
            logger.info("Shutting Down...")
            break
        except Exception as e:
            logger.info("Failed to connect with the services")
            logger.info("Retrying in 5 seconds")
            time.sleep(5)
            
if __name__ == "__main__":
    main()

    