from redis import Redis
from config import settings
from services.queue import queue
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

# ---------- Redis connection ----------

def get_redis_client():
    return Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        decode_responses=True
    )

redis_client = get_redis_client()


# ---------- Job status ----------

class JobStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# ---------- Job helpers ----------

def get_job_data(video_id: str):
    job = redis_client.get(video_id)
    return json.loads(job) if job else None


def update_job_status(video_id: str, status: str):
    job_data = get_job_data(video_id)
    if not job_data:
        return

    job_data["status"] = status
    job_data["updated_at"] = datetime.now().isoformat()
    redis_client.set(video_id, json.dumps(job_data))


# ---------- Outbox Worker ----------

class RedisClient:
    STREAM_NAME = "outbox:video_jobs"
    GROUP_NAME = "publishers"

    def __init__(self):
        self.redis_client = get_redis_client()
        self._create_consumer_group()

    def _create_consumer_group(self):
        """
        Create consumer group if it doesn't exist.
        Safe to call multiple times.
        """
        try:
            self.redis_client.xgroup_create(
                name=self.STREAM_NAME,
                groupname=self.GROUP_NAME,
                id="0",
                mkstream=True
            )
            logger.info("Redis consumer group created")
        except Exception as e:
            # BUSYGROUP means it already exists — which is fine
            if "BUSYGROUP" in str(e):
                logger.info("Redis consumer group already exists")
            else:
                raise

    def outbox_worker(self):
        consumer_name = "publisher-1"

        logger.info("Outbox worker started")

        while True:
            try:
                messages = self.redis_client.xreadgroup(
                    groupname=self.GROUP_NAME,
                    consumername=consumer_name,
                    streams={self.STREAM_NAME: ">"},
                    count=10,
                    block=5000  # ms
                )

                if not messages:
                    continue

                for stream_name, entries in messages:
                    for entry_id, data in entries:
                        self._process_message(entry_id, data)

            except Exception as e:
                logger.error(f"Outbox worker error: {str(e)}")

    def _process_message(self, entry_id, data):
        try:
            video_id = data["video_id"]
            video_path = data["video_path"]

            # 1. Publish to RabbitMQ
            queue.publish_extraction_task(video_id, video_path)

            # 2. Update job status
            update_job_status(video_id, JobStatus.PROCESSING)

            # 3. ACK the stream entry
            self.redis_client.xack(
                self.STREAM_NAME,
                self.GROUP_NAME,
                entry_id
            )

            logger.info(f"Published job {video_id} to RabbitMQ")

        except Exception as e:
            # DO NOT ACK — Redis will retry
            logger.error(
                f"Failed to process outbox message {entry_id}: {str(e)}"
            )
            
