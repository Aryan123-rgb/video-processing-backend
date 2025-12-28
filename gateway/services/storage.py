from pymongo import MongoClient
import uuid
from pathlib import Path
from config import settings
from typing import BinaryIO

def get_mongodb_connection():
    client = MongoClient(
        host=settings.mongodb_host,
        port=settings.mongodb_port,
        serverSelectionTimeoutMS=5000,
    )
    db = client[settings.mongodb_db]
    collection = db[settings.mongo_collection]
    return collection

class StorageService:
    def __init__(self):
        self.base_path = Path(settings.storage_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.db = get_mongodb_connection()

    def save_video(self, file: BinaryIO, filename: str) -> tuple[str, str]:
        video_id = str(uuid.uuid4())
        file_ext = Path(filename).suffix.lower()
        video_filename = f"{video_id}{file_ext}"
        video_path = self.base_path / video_filename
        
        with open(video_path, 'wb') as f:
            f.write(file.read())
            
        return video_id, str(video_path)
    
    def get_subtitles(self, video_id: str):
        subtitle = self.db.find_one({"video_id": video_id})
        return subtitle 
    
storage_service = StorageService()
    
    