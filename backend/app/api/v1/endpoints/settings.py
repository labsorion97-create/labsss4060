"""
ORIONIS API v1 - Settings Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.core.database import get_db
from app.core.security import get_current_token
from app.services.auth_service import AuthService
from app.services.settings_service import SettingsService
from app.schemas.schemas import (
    UserSettingsUpdate, UserSettingsResponse,
    TenantSettingsUpdate, TenantSettingsResponse,
    AIModelSettingsUpdate, AIModelSettingsResponse,
    SecuritySettingsUpdate, SecuritySettingsResponse
)

router = APIRouter(prefix="/settings", tags=["Settings"])


async def get_user_context(token: str, db: AsyncSession):
    """Helper to get user and tenant from token"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(token)
    return user.id, user.current_tenant.id if user.current_tenant else None


# ============== PROFILE ==============

@router.get("/profile", response_model=UserSettingsResponse)
async def get_profile_settings(
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Get user profile settings"""
    user_id, _ = await get_user_context(token, db)
    service = SettingsService(db)
    return await service.get_user_settings(user_id)


@router.put("/profile", response_model=UserSettingsResponse)
async def update_profile_settings(
    data: UserSettingsUpdate,
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Update user profile settings"""
    user_id, _ = await get_user_context(token, db)
    service = SettingsService(db)
    return await service.update_user_settings(user_id, data)


# ============== COMPANY ==============

@router.get("/company")
async def get_company_settings(
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Get company/branding settings"""
    _, tenant_id = await get_user_context(token, db)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="No tenant context")
    
    service = SettingsService(db)
    return await service.get_company_settings(tenant_id)


@router.put("/company")
async def update_company_settings(
    data: Dict[str, Any],
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Update company/branding settings"""
    _, tenant_id = await get_user_context(token, db)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="No tenant context")
    
    service = SettingsService(db)
    return await service.update_company_settings(tenant_id, data)


# ============== AI MODELS ==============

@router.get("/ai-models", response_model=AIModelSettingsResponse)
async def get_ai_model_settings(
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Get AI model settings"""
    _, tenant_id = await get_user_context(token, db)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="No tenant context")
    
    service = SettingsService(db)
    return await service.get_ai_settings(tenant_id)


@router.put("/ai-models", response_model=AIModelSettingsResponse)
async def update_ai_model_settings(
    data: AIModelSettingsUpdate,
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Update AI model settings"""
    _, tenant_id = await get_user_context(token, db)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="No tenant context")
    
    service = SettingsService(db)
    return await service.update_ai_settings(tenant_id, data)


@router.get("/ai-models/available")
async def get_available_models(
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Get available AI models"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = SettingsService(db)
    return await service.get_available_models()


# ============== TENANT ==============

@router.get("/tenant", response_model=TenantSettingsResponse)
async def get_tenant_settings(
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Get tenant settings"""
    _, tenant_id = await get_user_context(token, db)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="No tenant context")
    
    service = SettingsService(db)
    return await service.get_tenant_settings(tenant_id)


@router.put("/tenant", response_model=TenantSettingsResponse)
async def update_tenant_settings(
    data: TenantSettingsUpdate,
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Update tenant settings"""
    _, tenant_id = await get_user_context(token, db)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="No tenant context")
    
    service = SettingsService(db)
    return await service.update_tenant_settings(tenant_id, data)


# ============== SECURITY ==============

@router.get("/security", response_model=SecuritySettingsResponse)
async def get_security_settings(
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Get security settings"""
    _, tenant_id = await get_user_context(token, db)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="No tenant context")
    
    service = SettingsService(db)
    return await service.get_security_settings(tenant_id)


@router.put("/security", response_model=SecuritySettingsResponse)
async def update_security_settings(
    data: SecuritySettingsUpdate,
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Update security settings"""
    _, tenant_id = await get_user_context(token, db)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="No tenant context")
    
    service = SettingsService(db)
    return await service.update_security_settings(tenant_id, data)
