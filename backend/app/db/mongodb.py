import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("phishing_shield.db")

MONGODB_URI = os.getenv("MONGODB_URI", os.getenv("MONGO_URL", ""))
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "alerts")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "alerts")

_client = None
_db = None
_collection = None
_connected = False
_in_memory_alerts: List[Dict[str, Any]] = []

def init_db():
    global _client, _db, _collection, _connected
    if not MONGODB_URI:
        logger.info("No MONGODB_URI configured. Running in in-memory mode for alerts.")
        _connected = False
        return

    try:
        from pymongo import MongoClient
        _client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=4000,
            connectTimeoutMS=4000
        )
        # Test connection
        _client.admin.command('ping')
        _db = _client[MONGODB_DB_NAME]
        _collection = _db[MONGODB_COLLECTION]
        _connected = True
        logger.info(f"Connected to MongoDB Atlas: database '{MONGODB_DB_NAME}', collection '{MONGODB_COLLECTION}'")
    except Exception as e:
        logger.warning(f"Could not connect to MongoDB ({e}). Falling back to in-memory alerts storage.")
        _connected = False

def is_connected() -> bool:
    return _connected

def save_alert(alert_data: Dict[str, Any]) -> Dict[str, Any]:
    global _in_memory_alerts
    
    # Add created_at timestamp if missing
    if "created_at" not in alert_data:
        alert_data["created_at"] = datetime.utcnow().isoformat()
    
    # Store in memory for instant local retrieval
    _in_memory_alerts.insert(0, alert_data)
    if len(_in_memory_alerts) > 100:
        _in_memory_alerts = _in_memory_alerts[:100]

    # If MongoDB is connected, save to MongoDB collection
    if _connected and _collection is not None:
        try:
            # Create a clean copy for Mongo
            doc = dict(alert_data)
            # Remove any non-serializable objects
            _collection.insert_one(doc)
            # remove _id string representation for return
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
        except Exception as e:
            logger.error(f"Error saving alert to MongoDB: {e}")

    return alert_data

def get_recent_alerts(limit: int = 50) -> List[Dict[str, Any]]:
    if _connected and _collection is not None:
        try:
            cursor = _collection.find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
            docs = list(cursor)
            if docs:
                return docs
        except Exception as e:
            logger.error(f"Error reading alerts from MongoDB: {e}")

    # Fallback to in-memory alerts
    return _in_memory_alerts[:limit]

# Attempt initial connection on import
init_db()
