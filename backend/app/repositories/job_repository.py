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
            # Phase 7: application lifecycle defaults
            "application_status": "draft",
            "notes": None,
            "status_updated_at": now,
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

    # ── Phase 7: Application History ──────────────────────────────────────────

    async def update_status(
        self, job_id: str, user_id: str, new_status: str
    ) -> Optional[Dict[str, Any]]:
        """Update the application_status for a job. Strict user_id ownership check."""
        now = datetime.now(timezone.utc)
        result = await self.collection.update_one(
            {"_id": job_id, "user_id": user_id},
            {"$set": {"application_status": new_status, "status_updated_at": now, "updated_at": now}},
        )
        if result.matched_count > 0:
            return await self.get_by_id(job_id, user_id)
        return None

    async def update_notes(
        self, job_id: str, user_id: str, notes: str
    ) -> Optional[Dict[str, Any]]:
        """Update the free-text notes for a job application."""
        now = datetime.now(timezone.utc)
        result = await self.collection.update_one(
            {"_id": job_id, "user_id": user_id},
            {"$set": {"notes": notes or None, "updated_at": now}},
        )
        if result.matched_count > 0:
            return await self.get_by_id(job_id, user_id)
        return None

    async def list_by_status(
        self, user_id: str, status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List all applications for a user, optionally filtered by application_status."""
        query: Dict[str, Any] = {"user_id": user_id}
        if status_filter:
            query["application_status"] = status_filter
        cursor = self.collection.find(query).sort("updated_at", -1)
        return await cursor.to_list(length=500)

    async def get_stats(self, user_id: str) -> Dict[str, int]:
        """Return count of applications per status for a user."""
        from app.schemas.job import ApplicationStatus
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$application_status", "count": {"$sum": 1}}},
        ]
        cursor = self.collection.aggregate(pipeline)
        raw = await cursor.to_list(length=50)
        # Ensure all statuses are represented (even at 0)
        stats: Dict[str, int] = {s.value: 0 for s in ApplicationStatus}
        for row in raw:
            key = row.get("_id") or "draft"
            if key in stats:
                stats[key] = row["count"]
        return stats
