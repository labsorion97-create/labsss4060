"""
ORIONIS API v1 - Auth Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_token
from app.services.auth_service import AuthService
from app.schemas.schemas import (
    LoginRequest, RegisterRequest, TokenResponse, RefreshTokenRequest,
    UserResponse, UserWithTenant, OAuthSessionRequest, Enable2FAResponse, Verify2FARequest
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    service = AuthService(db)
    user, tenant = await service.register(data)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    """Login and get access tokens"""
    service = AuthService(db)
    user, tenant, tokens = await service.login(data)
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=tokens.access_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7*24*60*60,
        path="/"
    )
    
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Refresh access token"""
    service = AuthService(db)
    return await service.refresh_token(data.refresh_token)


@router.post("/logout")
async def logout(
    response: Response,
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Logout and invalidate session"""
    if token:
        service = AuthService(db)
        await service.logout(token)
    
    response.delete_cookie(key="session_token", path="/")
    return {"success": True, "message": "Logged out successfully"}


@router.get("/me", response_model=UserWithTenant)
async def get_me(
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Get current user"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = AuthService(db)
    return await service.get_current_user(token)


@router.post("/session", response_model=UserWithTenant)
async def oauth_session(
    data: OAuthSessionRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """Exchange OAuth session for tokens"""
    service = AuthService(db)
    user, tenant, tokens = await service.oauth_exchange(data.session_id)
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=tokens.access_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7*24*60*60,
        path="/"
    )
    
    return await service.get_current_user(tokens.access_token)


@router.post("/2fa/enable", response_model=Enable2FAResponse)
async def enable_2fa(
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Enable 2FA for current user"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = AuthService(db)
    user = await service.get_current_user(token)
    secret, uri = await service.enable_2fa(user.id)
    
    return Enable2FAResponse(secret=secret, qr_code=uri)


@router.post("/2fa/confirm")
async def confirm_2fa(
    data: Verify2FARequest,
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Confirm and activate 2FA"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = AuthService(db)
    user = await service.get_current_user(token)
    await service.confirm_2fa(user.id, data.code)
    
    return {"success": True, "message": "2FA enabled"}


@router.post("/2fa/disable")
async def disable_2fa(
    data: Verify2FARequest,
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Disable 2FA"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = AuthService(db)
    user = await service.get_current_user(token)
    await service.disable_2fa(user.id, data.code)
    
    return {"success": True, "message": "2FA disabled"}
