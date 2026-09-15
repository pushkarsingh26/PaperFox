from typing import Any, Dict
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.core.database import get_database
from app.core.security import decode_token
from app.repositories.profile_repository import ProfileRepository
from app.repositories.resume_repository import ResumeRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.repositories.job_repository import JobRepository
from app.services.auth_service import AuthService
from app.services.profile_service import ProfileService
from app.services.resume_service import ResumeService
from app.services.user_service import UserService
from app.services.job_service import JobService
from app.services.job_resume_service import JobResumeService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_user_repository() -> UserRepository:
    db = get_database()
    return UserRepository(db["users"])


def get_session_repository() -> SessionRepository:
    db = get_database()
    return SessionRepository(db["sessions"])


def get_profile_repository() -> ProfileRepository:
    db = get_database()
    return ProfileRepository(db["candidate_profiles"])


def get_resume_repository() -> ResumeRepository:
    db = get_database()
    return ResumeRepository(db["resume_artifacts"])


def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(user_repo)


def get_profile_service(
    profile_repo: ProfileRepository = Depends(get_profile_repository),
) -> ProfileService:
    return ProfileService(profile_repo)


def get_resume_service(
    resume_repo: ResumeRepository = Depends(get_resume_repository),
    profile_repo: ProfileRepository = Depends(get_profile_repository),
) -> ResumeService:
    return ResumeService(resume_repo, profile_repo)


def get_job_repository() -> JobRepository:
    db = get_database()
    return JobRepository(db["job_applications"])


def get_job_service(
    job_repo: JobRepository = Depends(get_job_repository),
    profile_repo: ProfileRepository = Depends(get_profile_repository),
) -> JobService:
    return JobService(job_repo, profile_repo)


def get_job_resume_service(
    job_repo: JobRepository = Depends(get_job_repository),
) -> JobResumeService:
    return JobResumeService(job_repo)


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    session_repo: SessionRepository = Depends(get_session_repository),
) -> AuthService:
    return AuthService(user_repo, session_repo)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
) -> Dict[str, Any]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token, settings.SECRET_KEY)
    if not payload or payload.get("type") != "access":
        raise credentials_exception

    user_id: str = payload.get("sub")
    if not user_id:
        raise credentials_exception

    user = await user_service.get_by_id(user_id)
    if not user:
        raise credentials_exception

    return user
