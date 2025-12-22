from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routes import video
import logging
from services.redis_client import get_redis_client
from services.queue import get_rabbitmq_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting API Gateway...")
    
    redis_client = get_redis_client()
    redis_client.ping()
    logger.info("Redis connection established")
    
    rabbitmq_connection = get_rabbitmq_connection()
    logger.info("RabbitMQ Connection Established")
    
    yield
    
    logger.info("Shutting down API gateway")
    rabbitmq_connection.close()
    redis_client.close()
    

app = FastAPI(
    title="Video Subtitle extractor API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(video.router, prefix="/api/v1", tags=["videos"])

@app.get('/health')
def health_check():
    return {
        "status": "healthy"
    }