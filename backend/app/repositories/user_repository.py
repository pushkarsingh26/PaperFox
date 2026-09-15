from datetime import datetime, timezone
from typing import Any, Dict, Optional
# pyrefly: ignore [missing-import]
from motor.motor_asyncio import AsyncIOMotorCollection
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection)

    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        normalized_email = email.strip().lower()
        return await self.collection.find_one({"email": normalized_email})

    async def update_last_login(self, user_id: str) -> Optional[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        return await self.update(user_id, {"last_login": now, "updated_at": now})
