from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_pass: str = "guest"
    rabbitmq_ffmpeg_extractor_queue: str = "ffmpeg_extractor_queue"
    
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    class Config:
        env_file = ".env"

settings = Settings()