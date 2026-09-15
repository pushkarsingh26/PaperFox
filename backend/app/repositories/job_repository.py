import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorCollection
from app.repositories.base import BaseRepository


class JobRepository(BaseRepository):
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection)

    async def create_job(self, user_id: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        job_id = str(uuid.uuid4())
        doc = {
            "_id": job_id,
            "user_id": user_id,
            "company_name": job_data["company_name"],
            "role_title": job_data["role_title"],
            "job_description": job_data["job_description"],
            "job_url": job_data.get("job_url"),
            "location": job_data.get("location"),
            "requirements": None,
            "analysis_provider": None,
            "analysis_model": None,
            "is_analyzed": False,
            "created_at": now,
            "updated_at": now
        }
        await self.collection.insert_one(doc)
        return doc

    async def get_by_id(self, job_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"_id": job_id, "user_id": user_id})

    async def list_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        cursor = self.collection.find({"user_id": user_id}).sort("created_at", -1)
        return await cursor.to_list(length=500)

    async def update_job(self, job_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        update_data["updated_at"] = datetime.now(timezone.utc)
        result = await self.collection.update_one(
            {"_id": job_id, "user_id": user_id},
            {"$set": update_data}
        )
        if result.matched_count > 0:
            return await self.get_by_id(job_id, user_id)
        return None

    async def delete_job(self, job_id: str, user_id: str) -> bool:
        result = await self.collection.delete_one({"_id": job_id, "user_id": user_id})
        return result.deleted_count > 0

    async def upsert_job_resume_artifact(
        self, job_id: str, user_id: str, artifact_dict: dict
    ) -> dict | None:
        """
        Persist (or overwrite) the Phase 6 job_resume_artifact subdocument
        inside the job_applications document. Always overwrites the previous artifact.
        """
        update_data = {
            "job_resume_artifact": artifact_dict,
            "is_resume_generated": artifact_dict.get("status") in ("success", "overflow", "compiler_unavailable"),
            "updated_at": datetime.now(timezone.utc),
        }
        result = await self.collection.update_one(
            {"_id": job_id, "user_id": user_id},
            {"$set": update_data},
        )
        if result.matched_count > 0:
            return await self.get_by_id(job_id, user_id)
        return None

    async def get_job_resume_artifact(self, job_id: str, user_id: str) -> dict | None:
        """Retrieve the stored Phase 6 job_resume_artifact for a job application."""
        doc = await self.get_by_id(job_id, user_id)
        if doc and doc.get("job_resume_artifact"):
            return doc["job_resume_artifact"]
        return None
