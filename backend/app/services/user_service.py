from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from app.core.security import get_password_hash
from app.models.user import UserInDB, serialize_doc
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def create_user(self, user_create: UserCreate) -> Dict[str, Any]:
        normalized_email = user_create.email.strip().lower()
        
        # Check if email already exists
        existing_user = await self.user_repo.get_by_email(normalized_email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists."
            )
        
        # Create user record
        password_hash = get_password_hash(user_create.password)
        user_db = UserInDB(email=normalized_email, password_hash=password_hash)
        
        user_doc = await self.user_repo.create(user_db.to_dict())
        return serialize_doc(user_doc)

    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        user_doc = await self.user_repo.get_by_email(email)
        return serialize_doc(user_doc)

    async def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        user_doc = await self.user_repo.get_by_id(user_id)
        return serialize_doc(user_doc)
