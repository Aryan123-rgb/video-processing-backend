from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_pass: str = "guest"
    rabbitmq_whisper_queue: str = "whisper_transcription_queue"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    mongodb_host: str = "localhost"
    mongodb_port: int = 27017
    mongodb_db: str = "video_subtitles"
    mongodb_collection: str = "subtitles"
    
    class Config:
        env_file = ".env"
        
settings = Settings()