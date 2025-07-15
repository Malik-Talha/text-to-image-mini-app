import pymongo
from pymongo.mongo_client import MongoClient
from typing import List, Optional
import logging
from config import settings

from models import ImageRecord

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            # print(f"Mongo URL: {settings.MONGODB_URL}")
            self.client = MongoClient(settings.MONGODB_URL)
            self.db = self.client[settings.DATABASE_NAME]
            self.collection = self.db[settings.COLLECTION_NAME]
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("✅ Connected to MongoDB successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            self.client = None
            self.db = None
            self.collection = None
            return False
    
    def save_image_record(self, image_record: ImageRecord) -> bool:
        """Save image record to database"""
        if self.collection is None:
            logger.warning("MongoDB not available, skipping save")
            return False
        
        try:
            self.collection.insert_one(image_record.model_dump())
            return True
        except Exception as e:
            logger.error(f"Failed to save image record: {e}")
            return False
    
    def get_images(self, limit: int = 20) -> List[dict]:
        """Get images from database"""
        if self.collection is None:
            return []
        
        try:
            cursor = self.collection.find().sort("created_at", -1).limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"Failed to fetch images: {e}")
            return []
    
    def get_prompt_history(self) -> List[dict]:
        """Get prompt history"""
        if self.collection is None:
            return []
        
        try:
            cursor = self.collection.find(
                {},
                {"prompt": 1, "expected_style": 1, "created_at": 1}
            ).sort("created_at", -1)
            return list(cursor)
        except Exception as e:
            logger.error(f"Failed to fetch prompt history: {e}")
            return []
    
    def count_images(self) -> int:
        """Count total images"""
        if self.collection is None:
            return 0
        
        try:
            return self.collection.count_documents({})
        except Exception as e:
            logger.error(f"Failed to count images: {e}")
            return 0
    
    def delete_image_record(self, image_id: str) -> bool:
        """Delete image record from database"""
        if self.collection is None:
            return False
        
        try:
            result = self.collection.delete_one({"id": image_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete image record: {e}")
            return False