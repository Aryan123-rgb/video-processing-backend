import os
import uuid
from pathlib import Path
from config import settings
from typing import BinaryIO

class StorageService:
    def __init__(self):
        self.base_path = Path(settings.storage_path)
        self.video_path = self.base_path / "videos"
        self.subtitle_path = self.base_path / "subtitles"
        
        self.video_path.mkdir(parents=True, exist_ok=True)
        self.subtitle_path.mkdir(parents=True, exist_ok=True)

    def save_video(self, file: BinaryIO, filename: str) -> tuple[str, str]:
        video_id = str(uuid.uuid4())
        file_ext = Path(filename).suffix.lower()
        video_filename = f"{video_id}{file_ext}"
        video_path = self.video_path / video_filename
        
        with open(video_path, 'wb') as f:
            f.write(file.read())
            
        return video_id, str(video_path)
    
storage_service = StorageService()
    
    