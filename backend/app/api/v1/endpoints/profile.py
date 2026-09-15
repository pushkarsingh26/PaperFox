from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_current_user, get_profile_service
from app.schemas.auth import MessageResponse
from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profile", tags=["Candidate Profile"])


@router.get("", response_model=ProfileResponse)
async def get_my_profile(
    current_user: dict = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
):
    """Retrieve the candidate profile owned by the authenticated user."""
    user_id = current_user["id"]
    profile = await profile_service.get_profile(user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found.",
        )
    return profile


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_or_upsert_profile(
    profile_in: ProfileCreate,
    current_user: dict = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
):
    """Create or overwrite candidate profile for authenticated user."""
    user_id = current_user["id"]
    profile_dict = profile_in.model_dump(mode="json")
    saved_profile = await profile_service.save_profile(user_id, profile_dict)
    return saved_profile


@router.put("", response_model=ProfileResponse)
async def update_profile(
    profile_in: ProfileUpdate,
    current_user: dict = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
):
    """Update existing candidate profile for authenticated user."""
    user_id = current_user["id"]
    profile_dict = profile_in.model_dump(mode="json", exclude_unset=True)
    saved_profile = await profile_service.save_profile(user_id, profile_dict)
    return saved_profile


@router.delete("", response_model=MessageResponse)
async def delete_my_profile(
    current_user: dict = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
):
    """Delete candidate profile for authenticated user."""
    user_id = current_user["id"]
    deleted = await profile_service.delete_profile(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found.",
        )
    return MessageResponse(message="Candidate profile deleted successfully.")
