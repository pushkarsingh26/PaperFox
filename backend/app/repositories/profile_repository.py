from datetime import datetime, timezone
from typing import Any, Dict, Optional
from motor.motor_asyncio import AsyncIOMotorCollection
from app.repositories.base import BaseRepository


class ProfileRepository(BaseRepository):
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection)

    async def get_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"user_id": user_id})

    async def upsert_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        profile_data["updated_at"] = now

        existing = await self.get_by_user_id(user_id)
        if existing:
            await self.collection.update_one(
                {"user_id": user_id},
                {"$set": profile_data}
            )
        else:
            profile_data["user_id"] = user_id
            profile_data["created_at"] = now
            await self.collection.insert_one(profile_data)

        return await self.get_by_user_id(user_id)

    async def delete_by_user_id(self, user_id: str) -> bool:
        result = await self.collection.delete_one({"user_id": user_id})
        return result.deleted_count > 0
