from datetime import datetime, timezone
from typing import Any, Dict, Optional
from motor.motor_asyncio import AsyncIOMotorCollection
from app.repositories.base import BaseRepository


class ResumeRepository(BaseRepository):
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection)

    async def get_base_artifact(self, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"user_id": user_id, "type": "base"})

    async def upsert_base_artifact(
        self, user_id: str, artifact_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        artifact_data["updated_at"] = now
        artifact_data["type"] = "base"
        artifact_data["user_id"] = user_id

        existing = await self.get_base_artifact(user_id)
        if existing:
            await self.collection.update_one(
                {"_id": existing["_id"]},
                {"$set": artifact_data}
            )
        else:
            artifact_data["created_at"] = now
            await self.collection.insert_one(artifact_data)

        return await self.get_base_artifact(user_id)
