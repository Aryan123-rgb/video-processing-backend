from pymongo import MongoClient
from typing import Optional
from config import settings

def get_mongodb_connection():
    client = MongoClient(
        host=settings.mongodb_host,
        port=settings.mongodb_port,
        serverSelectionTimeoutMS=5000,
    )
    db = client[settings.mongodb_db]
    collection = db[settings.mongodb_collection]
    
    # indexing for fast lookups
    collection.create_index([("video_id", 1)], unique=True)
    return collection

class MongoDB:
    def __init__(self):
        self.db = get_mongodb_connection()
    
    def save_subtitles(self, video_id: str, subtitle_content: str):
        """
        Stores subtitles as:
        { video_id: <id>, subtitle: <srt_content> }
        """
        self.db.update_one(
            {"video_id": video_id},
            {"$set": {
                "subtitle": subtitle_content
            }},
            upsert=True
        )

mongodb = MongoDB()