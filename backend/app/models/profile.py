from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from bson import ObjectId


class CandidateProfileInDB:
    def __init__(
        self,
        user_id: str,
        personal_details: Dict[str, Any],
        candidate_type: str = "fresher",
        profile_status: str = "draft",
        internships: Optional[List[Dict[str, Any]]] = None,
        experience: Optional[List[Dict[str, Any]]] = None,
        education: Optional[List[Dict[str, Any]]] = None,
        projects: Optional[List[Dict[str, Any]]] = None,
        skills: Optional[List[Dict[str, Any]]] = None,
        certifications: Optional[List[Dict[str, Any]]] = None,
        section_order: Optional[List[str]] = None,
        completion_percentage: int = 0,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        _id: Optional[Any] = None,
    ):
        self.id = str(_id) if _id else None
        self.user_id = user_id
        self.personal_details = personal_details
        self.candidate_type = candidate_type
        self.profile_status = profile_status
        self.internships = internships or []
        self.experience = experience or []
        self.education = education or []
        self.projects = projects or []
        self.skills = skills or []
        self.certifications = certifications or []
        self.section_order = section_order
        self.completion_percentage = completion_percentage
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "user_id": self.user_id,
            "profile_status": self.profile_status,
            "personal_details": self.personal_details,
            "candidate_type": self.candidate_type,
            "internships": self.internships,
            "experience": self.experience,
            "education": self.education,
            "projects": self.projects,
            "skills": self.skills,
            "certifications": self.certifications,
            "section_order": self.section_order,
            "completion_percentage": self.completion_percentage,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self.id:
            data["_id"] = ObjectId(self.id)
        return data
