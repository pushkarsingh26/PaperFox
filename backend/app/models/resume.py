from datetime import datetime, timezone
from typing import Any, Dict, Optional
from bson import ObjectId


class ResumeArtifactInDB:
    def __init__(
        self,
        user_id: str,
        type: str = "base",
        latex_source: str = "",
        pdf_storage_reference: Optional[str] = None,
        page_count: int = 0,
        status: str = "draft",
        error_message: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        _id: Optional[Any] = None,
    ):
        self.id = str(_id) if _id else None
        self.user_id = user_id
        self.type = type
        self.latex_source = latex_source
        self.pdf_storage_reference = pdf_storage_reference
        self.page_count = page_count
        self.status = status
        self.error_message = error_message
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "user_id": self.user_id,
            "type": self.type,
            "latex_source": self.latex_source,
            "pdf_storage_reference": self.pdf_storage_reference,
            "page_count": self.page_count,
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self.id:
            data["_id"] = ObjectId(self.id)
        return data
