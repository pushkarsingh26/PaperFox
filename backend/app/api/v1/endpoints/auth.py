from typing import Optional
from fastapi import APIRouter, Depends, Header, status
from app.api.deps import get_auth_service, get_current_user, get_user_service
from app.schemas.auth import MessageResponse, RefreshTokenRequest, Token, UserLogin
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(
    user_in: UserCreate,
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Register a new candidate user and return access/refresh tokens."""
    created_user = await user_service.create_user(user_in)
    token_pair = await auth_service.issue_tokens(created_user["id"])
    return token_pair


@router.post("/login", response_model=Token)
async def login(
    login_in: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Authenticate user with email and password, returning access/refresh tokens."""
    user = await auth_service.authenticate_user(login_in)
    token_pair = await auth_service.issue_tokens(user["id"])
    return token_pair


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_in: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Validate refresh token and issue a new access/refresh token pair."""
    return await auth_service.refresh_tokens(refresh_in.refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    refresh_in: Optional[RefreshTokenRequest] = None,
    x_refresh_token: Optional[str] = Header(None, alias="X-Refresh-Token"),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Invalidate server-side refresh session."""
    token_to_revoke = None
    if refresh_in and refresh_in.refresh_token:
        token_to_revoke = refresh_in.refresh_token
    elif x_refresh_token:
        token_to_revoke = x_refresh_token

    if token_to_revoke:
        await auth_service.logout(token_to_revoke)

    return MessageResponse(message="Successfully logged out")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Fetch profile details of the currently authenticated user."""
    return current_user
