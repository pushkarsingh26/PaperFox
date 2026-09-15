from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from app.models.user import serialize_doc
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import ProfileCreate, ProfileUpdate


class ProfileService:
    def __init__(self, profile_repo: ProfileRepository):
        self.profile_repo = profile_repo

    @staticmethod
    def calculate_completion_percentage(profile_data: Dict[str, Any]) -> int:
        """
        Deterministic completion percentage calculation normalized to 100%.
        Does not penalize freshers without internships.
        """
        candidate_type = profile_data.get("candidate_type", "fresher")

        # Define section weights
        # Base requirements present for all candidates:
        # Personal details: 20
        # Candidate type: 10
        # Education: 20
        # Projects: 15
        # Skills: 10
        # Certifications: 5
        
        earned_points = 0
        total_possible = 0

        # 1. Personal Details (20 points)
        total_possible += 20
        personal = profile_data.get("personal_details", {})
        if personal and personal.get("full_name", "").strip():
            earned_points += 20

        # 2. Candidate Type (10 points)
        total_possible += 10
        if candidate_type in ["fresher", "experienced"]:
            earned_points += 10

        # 3. Education (20 points)
        total_possible += 20
        if profile_data.get("education") and len(profile_data["education"]) > 0:
            earned_points += 20

        # 4. Work Experience / Internship (20 points conditional)
        if candidate_type == "experienced":
            total_possible += 20
            if profile_data.get("experience") and len(profile_data["experience"]) > 0:
                earned_points += 20
        else:
            # Fresher logic: if internships exist, count them towards pool. If no internship, satisfied by choice.
            internships = profile_data.get("internships", [])
            if len(internships) > 0:
                total_possible += 20
                earned_points += 20
            else:
                # Requirement satisfied by choice, exclude from total_possible pool
                pass

        # 5. Projects (15 points)
        total_possible += 15
        if profile_data.get("projects") and len(profile_data["projects"]) > 0:
            earned_points += 15

        # 6. Skills (10 points)
        total_possible += 10
        if profile_data.get("skills") and len(profile_data["skills"]) > 0:
            earned_points += 10

        # 7. Certifications (5 points)
        total_possible += 5
        if profile_data.get("certifications") and len(profile_data["certifications"]) > 0:
            earned_points += 5

        if total_possible == 0:
            return 0

        percentage = int(round((earned_points / total_possible) * 100))
        return min(100, max(0, percentage))

    async def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.profile_repo.get_by_user_id(user_id)
        return serialize_doc(doc)

    async def save_profile(
        self, user_id: str, profile_in: Dict[str, Any]
    ) -> Dict[str, Any]:
        existing = await self.profile_repo.get_by_user_id(user_id)
        
        merged = existing.copy() if existing else {}
        # Merge top-level fields
        for key, value in profile_in.items():
            if value is not None:
                merged[key] = value

        merged["completion_percentage"] = self.calculate_completion_percentage(merged)
        
        saved_doc = await self.profile_repo.upsert_profile(user_id, merged)
        return serialize_doc(saved_doc)

    async def delete_profile(self, user_id: str) -> bool:
        return await self.profile_repo.delete_by_user_id(user_id)
