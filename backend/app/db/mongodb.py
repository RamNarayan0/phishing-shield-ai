import os
import time
import hashlib
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("phishing_shield.db")

# Configuration from Environment
DEFAULT_URI = "mongodb://127.0.0.1:27017"
DEFAULT_DB = "phishing_shield_ai"
DEFAULT_COLL = "analysis_history"

MONGODB_URI = os.getenv("MONGODB_URI", os.getenv("MONGO_URL", DEFAULT_URI))
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", os.getenv("MONGODB_DB_NAME", DEFAULT_DB))
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", DEFAULT_COLL)

_client = None
_db = None
_collection = None
_connected = False
_in_memory_alerts: List[Dict[str, Any]] = []

def get_collection():
    """Returns the currently active MongoDB collection."""
    return _collection

def get_db():
    """Returns the currently active MongoDB database."""
    return _db


def generate_fingerprint(raw_text: str, sender_id: Optional[str] = None, source_platform: Optional[str] = None) -> str:
    """
    Generates a deterministic SHA-256 fingerprint for source-specific duplicate detection.

    Fields defining duplicate identity:
    1. Normalized raw text: trimmed, lowercased, and collapsed whitespace.
    2. Normalized sender ID: trimmed and lowercased (if provided).
    3. Source platform: normalized identifier.
    """
    norm_text = " ".join((raw_text or "").strip().lower().split())
    norm_sender = (sender_id or "").strip().lower()
    norm_source = (source_platform or "").strip().lower()
    canonical = f"text:{norm_text}|sender:{norm_sender}|src:{norm_source}"
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

def generate_content_fingerprint(raw_text: str, sender_id: Optional[str] = None) -> str:
    """
    Generates a deterministic SHA-256 fingerprint representing the core threat payload,
    independent of ingress source platform, for cross-channel threat correlation.
    """
    norm_text = " ".join((raw_text or "").strip().lower().split())
    norm_sender = (sender_id or "").strip().lower()
    canonical = f"text:{norm_text}|sender:{norm_sender}"
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

def init_db(uri: Optional[str] = None, db_name: Optional[str] = None) -> bool:
    """
    Initializes the MongoDB connection, verifies reachability via ping,
    and ensures unique indexes for duplicate prevention are created.
    Dynamically respects MONGODB_DATABASE env var or db_name argument.
    """
    global _client, _db, _collection, _connected, MONGODB_DATABASE, MONGODB_URI

    target_uri = uri or os.getenv("MONGODB_URI", os.getenv("MONGO_URL", DEFAULT_URI))
    target_db = db_name or os.getenv("MONGODB_DATABASE", os.getenv("MONGODB_DB_NAME", DEFAULT_DB))

    MONGODB_URI = target_uri
    MONGODB_DATABASE = target_db

    if not target_uri:
        logger.info("No MONGODB_URI configured. Running in in-memory mode for alerts.")
        _connected = False
        return False

    try:
        from pymongo import MongoClient

        # Connection pooling and sensible short timeouts (2s) so backend never hangs
        _client = MongoClient(
            target_uri,
            serverSelectionTimeoutMS=2000,
            connectTimeoutMS=2000,
            maxPoolSize=50,
            minPoolSize=5
        )
        # Verify connection
        _client.admin.command("ping")
        _db = _client[target_db]
        _collection = _db[MONGODB_COLLECTION]

        # Enforce uniqueness via unique index on fingerprint
        _collection.create_index(
            [("fingerprint", 1)],
            unique=True,
            sparse=True,
            name="idx_analysis_fingerprint"
        )
        # Index for cross-source threat correlation
        _collection.create_index(
            [("content_fingerprint", 1)],
            sparse=True,
            name="idx_analysis_content_fingerprint"
        )
        # Fast chronological lookup indexes
        _collection.create_index(
            [("last_seen_at", -1)],
            name="idx_analysis_last_seen_at"
        )
        _collection.create_index(
            [("created_at", -1)],
            name="idx_analysis_created_at"
        )

        _connected = True
        logger.info(f"Connected to MongoDB: database '{target_db}', collection '{MONGODB_COLLECTION}' with unique fingerprint indexing.")
        return True
    except Exception as e:
        logger.warning(f"Could not connect to MongoDB at {sanitize_uri(target_uri)} ({type(e).__name__}). Falling back to in-memory alerts storage.")
        _client = None
        _db = None
        _collection = None
        _connected = False
        return False

def close_db():
    """Cleanly closes the MongoDB connection pool during shutdown."""
    global _client, _db, _collection, _connected
    if _client is not None:
        try:
            _client.close()
            logger.info("Closed MongoDB connection pool.")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}")
        finally:
            _client = None
            _db = None
            _collection = None
            _connected = False

def is_connected() -> bool:
    """Returns True if MongoDB is connected and initialized."""
    return _connected

def check_health() -> Dict[str, Any]:
    """
    Runs a live ping command and returns detailed connection health
    without leaking sensitive credentials or URI tokens.
    """
    if not _connected or _client is None:
        return {
            "status": "disconnected",
            "backend_storage": "in-memory-fallback",
            "database": MONGODB_DATABASE,
            "collection": MONGODB_COLLECTION,
            "message": "Local or remote MongoDB server is unreachable; running in-memory fallback."
        }
    try:
        start = time.time()
        _client.admin.command("ping")
        latency_ms = round((time.time() - start) * 1000, 2)
        return {
            "status": "connected",
            "backend_storage": "mongodb",
            "database": MONGODB_DATABASE,
            "collection": MONGODB_COLLECTION,
            "ping_latency_ms": latency_ms
        }
    except Exception as e:
        logger.error(f"MongoDB health ping failed: {e}")
        return {
            "status": "error",
            "backend_storage": "in-memory-fallback",
            "database": MONGODB_DATABASE,
            "error": "Ping failed; falling back to in-memory"
        }

def save_alert(alert_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Persists an analysis record to MongoDB with atomic duplicate prevention.

    If an identical message fingerprint already exists:
    - Atomically increments duplicate_count and updates last_seen_at.
    - Tracks observed delivery channels via observed_sources array.
    - Does NOT insert a duplicate document into the database.
    - Prevents race conditions through MongoDB's unique index.
    """
    global _in_memory_alerts

    now = datetime.now(timezone.utc).isoformat()
    if "created_at" not in alert_data:
        alert_data["created_at"] = now
    alert_data["last_seen_at"] = now

    # Generate deterministic fingerprints
    raw_text = alert_data.get("raw_text", "")
    sender_id = alert_data.get("sender_id")
    source_platform = alert_data.get("source_platform") or "Unknown"

    fingerprint = generate_fingerprint(raw_text, sender_id, source_platform)
    content_fingerprint = generate_content_fingerprint(raw_text, sender_id)

    alert_data["fingerprint"] = fingerprint
    alert_data["content_fingerprint"] = content_fingerprint
    alert_data.setdefault("observed_sources", [source_platform])

    # Handle In-Memory Storage & Deduplication (fallback)
    existing_mem = next((a for a in _in_memory_alerts if a.get("fingerprint") == fingerprint), None)
    if existing_mem:
        existing_mem["last_seen_at"] = now
        existing_mem["duplicate_count"] = existing_mem.get("duplicate_count", 1) + 1
        if source_platform not in existing_mem.setdefault("observed_sources", []):
            existing_mem["observed_sources"].append(source_platform)
        alert_data["duplicate_count"] = existing_mem["duplicate_count"]
        alert_data["observed_sources"] = existing_mem["observed_sources"]
        alert_data["is_duplicate"] = True
    else:
        alert_data["duplicate_count"] = 1
        alert_data["is_duplicate"] = False
        _in_memory_alerts.insert(0, alert_data)
        if len(_in_memory_alerts) > 100:
            _in_memory_alerts = _in_memory_alerts[:100]

    # Handle MongoDB Storage & Deduplication
    if _connected and _collection is not None:
        try:
            from pymongo.errors import DuplicateKeyError

            doc = dict(alert_data)
            # Remove MongoDB internal _id if present in incoming data
            doc.pop("_id", None)

            # Atomic Upsert: If document with fingerprint exists, update timestamps; otherwise insert.
            res = _collection.update_one(
                {"fingerprint": fingerprint},
                {
                    "$setOnInsert": {
                        "id": doc.get("id"),
                        "timestamp": doc.get("timestamp"),
                        "source_platform": doc.get("source_platform"),
                        "application_name": doc.get("application_name"),
                        "sender_id": doc.get("sender_id"),
                        "raw_text": doc.get("raw_text"),
                        "result": doc.get("result"),
                        "created_at": now,
                        "fingerprint": fingerprint,
                        "content_fingerprint": content_fingerprint
                    },
                    "$set": {
                        "last_seen_at": now
                    },
                    "$inc": {
                        "duplicate_count": 1
                    },
                    "$addToSet": {
                        "observed_sources": source_platform
                    }
                },
                upsert=True
            )

            if res.upserted_id is None:
                alert_data["is_duplicate"] = True
                # Query authoritative duplicate count and observed sources from DB
                updated = _collection.find_one(
                    {"fingerprint": fingerprint},
                    {"duplicate_count": 1, "observed_sources": 1, "last_seen_at": 1, "_id": 0}
                )
                if updated:
                    alert_data["duplicate_count"] = updated.get("duplicate_count", 1)
                    alert_data["observed_sources"] = updated.get("observed_sources", [source_platform])
                logger.info(f"Duplicate submission detected for fingerprint {fingerprint[:8]}... (count: {alert_data.get('duplicate_count')})")
            else:
                alert_data["is_duplicate"] = False
                alert_data["duplicate_count"] = 1
                logger.info(f"Saved new analysis record {fingerprint[:8]}... to MongoDB")

        except DuplicateKeyError:
            # Race condition safely handled: another concurrent worker inserted the same fingerprint
            alert_data["is_duplicate"] = True
            updated = _collection.find_one(
                {"fingerprint": fingerprint},
                {"duplicate_count": 1, "observed_sources": 1, "_id": 0}
            )
            if updated:
                alert_data["duplicate_count"] = updated.get("duplicate_count", 1)
                alert_data["observed_sources"] = updated.get("observed_sources", [source_platform])
            logger.info(f"Concurrent duplicate submission intercepted for fingerprint {fingerprint[:8]}")
        except Exception as e:
            logger.error(f"Error saving alert to MongoDB: {e}")
            # Ensure DB errors never cause analysis failure

    return alert_data

def get_recent_alerts(limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieves recent unique analysis alerts, sorted most recently observed first."""
    if _connected and _collection is not None:
        try:
            cursor = _collection.find({}, {"_id": 0}).sort([("last_seen_at", -1), ("created_at", -1)]).limit(limit)
            docs = list(cursor)
            if docs:
                return docs
        except Exception as e:
            logger.error(f"Error reading alerts from MongoDB: {e}")

    # Fallback to in-memory alerts
    return _in_memory_alerts[:limit]

def sanitize_uri(uri: str) -> str:
    """Masks username and password from MongoDB URI for safe logging."""
    if not uri:
        return ""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(uri)
        if parsed.password:
            return uri.replace(f":{parsed.password}@", ":****@")
        return uri
    except Exception:
        return "mongodb://[sanitized]"

# Auto-initialize on module load
init_db()
