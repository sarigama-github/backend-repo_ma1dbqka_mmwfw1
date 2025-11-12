import os
from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from bson import ObjectId, Binary

DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "appdb")

_client: AsyncIOMotorClient = AsyncIOMotorClient(DATABASE_URL)
db: AsyncIOMotorDatabase = _client[DATABASE_NAME]

async def create_document(collection: str, data: Dict[str, Any]) -> str:
    doc = {**data, "created_at": data.get("created_at") or __import__("datetime").datetime.utcnow(), "updated_at": data.get("updated_at") or __import__("datetime").datetime.utcnow()}
    result = await db[collection].insert_one(doc)
    return str(result.inserted_id)

async def get_documents(collection: str, filter_dict: Optional[Dict[str, Any]] = None, limit: int = 100, sort: Optional[List] = None) -> List[Dict[str, Any]]:
    cursor = db[collection].find(filter_dict or {})
    if sort:
        cursor = cursor.sort(sort)
    if limit:
        cursor = cursor.limit(limit)
    items: List[Dict[str, Any]] = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        items.append(doc)
    return items

async def get_document(collection: str, _id: str) -> Optional[Dict[str, Any]]:
    doc = await db[collection].find_one({"_id": ObjectId(_id)})
    if not doc:
        return None
    doc["id"] = str(doc.pop("_id"))
    return doc

async def update_document(collection: str, _id: str, data: Dict[str, Any]) -> bool:
    data["updated_at"] = __import__("datetime").datetime.utcnow()
    res = await db[collection].update_one({"_id": ObjectId(_id)}, {"$set": data})
    return res.modified_count > 0

async def delete_document(collection: str, _id: str) -> bool:
    res = await db[collection].delete_one({"_id": ObjectId(_id)})
    return res.deleted_count > 0

async def save_document_file(metadata: Dict[str, Any], content: bytes) -> str:
    coll = db["documents"]
    payload = {**metadata, "content": Binary(content), "created_at": __import__("datetime").datetime.utcnow()}
    result = await coll.insert_one(payload)
    return str(result.inserted_id)
