from pathlib import Path
from config import settings

class Storage:
    def __init__(self):
        self.base_path = Path(settings.storage_path)
        self.video_path = self.base_path / "videos"
        self.subtitle_path = self.base_path / "subtitles"
        
        self.video_path.mkdir(exist_ok=True, parents=True)
        self.subtitle_path.mkdir(exist_ok=True, parents=True)
        
    def get_subtitle_path(self, video_id: str):
        subtitle_path = self.subtitle_path / f"{video_id}.srt"
        return subtitle_path
    
    def save_subtitle(self, video_id: str, subtitle_content: str):
        subtitle_path = self.subtitle_path / f"{video_id}.srt"
        with open(subtitle_path, 'w', encoding='utf-8') as f:
            f.write(subtitle_content)
        return str(subtitle_path)
    
storage_service = Storage()