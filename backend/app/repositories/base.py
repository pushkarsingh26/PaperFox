from typing import Any, Dict, List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection


class BaseRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def get_by_id(self, id_str: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(id_str):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(id_str)})
        return doc

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.collection.insert_one(data)
        doc = await self.collection.find_one({"_id": result.inserted_id})
        return doc

    async def update(self, id_str: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(id_str):
            return None
        await self.collection.update_one(
            {"_id": ObjectId(id_str)},
            {"$set": update_data}
        )
        return await self.get_by_id(id_str)

    async def delete(self, id_str: str) -> bool:
        if not ObjectId.is_valid(id_str):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(id_str)})
        return result.deleted_count > 0
