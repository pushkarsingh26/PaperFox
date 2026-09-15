from datetime import datetime, timezone
from typing import Any, Dict
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
    verify_password,
)
from app.models.user import serialize_doc
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import Token, UserLogin


class AuthService:
    def __init__(self, user_repo: UserRepository, session_repo: SessionRepository):
        self.user_repo = user_repo
        self.session_repo = session_repo

    async def authenticate_user(self, login_data: UserLogin) -> Dict[str, Any]:
        normalized_email = login_data.email.strip().lower()
        user = await self.user_repo.get_by_email(normalized_email)
        
        # Generic error message to prevent account enumeration
        invalid_cred_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        if not user:
            raise invalid_cred_exception

        if not verify_password(login_data.password, user["password_hash"]):
            raise invalid_cred_exception

        user_id = str(user["_id"])
        await self.user_repo.update_last_login(user_id)
        return serialize_doc(user)

    async def issue_tokens(self, user_id: str) -> Token:
        access_token = create_access_token(subject=user_id)
        refresh_token, expires_at = create_refresh_token(subject=user_id)
        
        token_hash = hash_token(refresh_token)
        await self.session_repo.create_session(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    async def refresh_tokens(self, raw_refresh_token: str) -> Token:
        unauthorized_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

        payload = decode_token(raw_refresh_token, settings.REFRESH_SECRET_KEY)
        if not payload or payload.get("type") != "refresh":
            raise unauthorized_exception

        user_id = payload.get("sub")
        if not user_id:
            raise unauthorized_exception

        # Check server-side session
        token_hash = hash_token(raw_refresh_token)
        session = await self.session_repo.get_by_token_hash(token_hash)
        
        if not session or session.get("is_revoked"):
            raise unauthorized_exception

        # Ensure session hasn't expired in DB
        expires_at = session.get("expires_at")
        if isinstance(expires_at, datetime) and expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
            
        if expires_at and expires_at < datetime.now(timezone.utc):
            await self.session_repo.revoke_by_token_hash(token_hash)
            raise unauthorized_exception

        # Revoke old session token (rotate token)
        await self.session_repo.revoke_by_token_hash(token_hash)

        # Issue new token pair
        return await self.issue_tokens(user_id)

    async def logout(self, raw_refresh_token: str) -> bool:
        if not raw_refresh_token:
            return False
        token_hash = hash_token(raw_refresh_token)
        return await self.session_repo.revoke_by_token_hash(token_hash)
