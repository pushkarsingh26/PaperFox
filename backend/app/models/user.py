from datetime import datetime, timezone
from typing import Any, Dict, Optional
from bson import ObjectId


def serialize_doc(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Helper to convert BSON ObjectId and datetimes for JSON serialization."""
    if not doc:
        return None
    result = dict(doc)
    if "_id" in result and isinstance(result["_id"], ObjectId):
        result["id"] = str(result["_id"])
        result["_id"] = str(result["_id"])
    return result


class UserInDB:
    def __init__(
        self,
        email: str,
        password_hash: str,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        last_login: Optional[datetime] = None,
        _id: Optional[Any] = None
    ):
        self.id = str(_id) if _id else None
        self.email = email.strip().lower()
        self.password_hash = password_hash
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
        self.last_login = last_login

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "email": self.email,
            "password_hash": self.password_hash,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_login": self.last_login
        }
        if self.id:
            data["_id"] = ObjectId(self.id)
        return data


class SessionInDB:
    def __init__(
        self,
        user_id: str,
        token_hash: str,
        expires_at: datetime,
        created_at: Optional[datetime] = None,
        is_revoked: bool = False,
        _id: Optional[Any] = None
    ):
        self.id = str(_id) if _id else None
        self.user_id = user_id
        self.token_hash = token_hash
        self.expires_at = expires_at
        self.created_at = created_at or datetime.now(timezone.utc)
        self.is_revoked = is_revoked

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "user_id": self.user_id,
            "token_hash": self.token_hash,
            "expires_at": self.expires_at,
            "created_at": self.created_at,
            "is_revoked": self.is_revoked
        }
        if self.id:
            data["_id"] = ObjectId(self.id)
        return data
