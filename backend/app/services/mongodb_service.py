from pymongo import MongoClient
import os
from typing import Dict
import logging
from datetime import datetime
from urllib.parse import quote_plus

class MongoDBService:
    def __init__(self):
        # Get MongoDB connection details from environment variables
        mongodb_host = os.getenv("MONGODB_HOST", "localhost")
        mongodb_port = os.getenv("MONGODB_PORT", "27017")
        mongodb_user = os.getenv("MONGODB_USER", "admin")
        mongodb_password = os.getenv("MONGODB_PASSWORD", "password123")
        
        # Construct MongoDB URI with credentials
        mongodb_uri = f"mongodb://{quote_plus(mongodb_user)}:{quote_plus(mongodb_password)}@{mongodb_host}:{mongodb_port}"
        
        try:
            self.client = MongoClient(mongodb_uri)
            # Test connection
            self.client.admin.command('ping')
            logging.info("Successfully connected to MongoDB")
        except Exception as e:
            logging.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
            
        self.db = self.client.hr_documents
        self.collection = self.db.documents

    def store_document(self, hr_data: Dict) -> str:
        try:
            # Add timestamp
            hr_data["created_at"] = datetime.utcnow()
            
            # Insert document
            result = self.collection.insert_one(hr_data)
            
            # Return the inserted document's ID
            return str(result.inserted_id)
        except Exception as e:
            logging.error(f"Error storing document in MongoDB: {str(e)}")
            raise

    def __del__(self):
        try:
            if hasattr(self, 'client'):
                self.client.close()
        except Exception as e:
            logging.error(f"Error closing MongoDB connection: {str(e)}") 