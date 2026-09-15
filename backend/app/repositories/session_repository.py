from datetime import datetime, timezone
from typing import Any, Dict, Optional
# pyrefly: ignore [missing-import]
from motor.motor_asyncio import AsyncIOMotorCollection
from app.repositories.base import BaseRepository


class SessionRepository(BaseRepository):
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection)

    async def create_session(
        self, user_id: str, token_hash: str, expires_at: datetime
    ) -> Dict[str, Any]:
        data = {
            "user_id": user_id,
            "token_hash": token_hash,
            "expires_at": expires_at,
            "created_at": datetime.now(timezone.utc),
            "is_revoked": False,
        }
        return await self.create(data)

    async def get_by_token_hash(self, token_hash: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"token_hash": token_hash, "is_revoked": False})

    async def revoke_by_token_hash(self, token_hash: str) -> bool:
        result = await self.collection.update_one(
            {"token_hash": token_hash},
            {"$set": {"is_revoked": True, "revoked_at": datetime.now(timezone.utc)}}
        )
        return result.modified_count > 0

    async def revoke_all_user_sessions(self, user_id: str) -> int:
        result = await self.collection.update_many(
            {"user_id": user_id, "is_revoked": False},
            {"$set": {"is_revoked": True, "revoked_at": datetime.now(timezone.utc)}}
        )
        return result.modified_count
