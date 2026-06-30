# backend/fastapi_app/mongo.py
import os
from typing import List, Dict, Any
from pymongo import MongoClient
from pymongo.collection import Collection

# Fallback to local if not loaded via config module
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

# Initialize client and target database
client = MongoClient(MONGO_URL)
db = client["dataflow_raw"]

def get_events_collection() -> Collection:
    """Returns the raw_events collection."""
    return db["raw_events"]

def insert_event(event_dict: Dict[str, Any]) -> str:
    """Inserts a raw event document and returns the inserted_id as a string."""
    collection = get_events_collection()
    result = collection.insert_one(event_dict)
    return str(result.inserted_id)

def get_events_by_project(project_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Queries and returns a list of events filtered by project_id."""
    collection = get_events_collection()
    cursor = collection.find({"project_id": project_id}).limit(limit)
    
    events = []
    for doc in cursor:
        # Convert ObjectId to string for easier JSON serialization downstream
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        events.append(doc)
        
    return events