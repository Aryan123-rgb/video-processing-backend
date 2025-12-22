from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_pass: str = "guest"
    rabbitmq_queue: str = "video_processing"
    
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    storage_path: str = ".././storage"
    max_file_size: int = 500 * 1024 * 1024
    allowed_extension: set = {".mov", ".mp4", ".mkv"}
    
    class Config:
        env_file = ".env"

settings = Settings()