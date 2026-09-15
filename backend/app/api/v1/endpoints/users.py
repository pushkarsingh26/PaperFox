from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def read_user_me(current_user: dict = Depends(get_current_user)):
    """Fetch profile details for the currently authenticated user."""
    return current_user
