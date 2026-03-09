"""
ORIONIS Settings Service
"""
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import User, UserSettings, Tenant, TenantSettings, AIModelSettings, SecuritySettings, BillingSettings
from app.schemas.schemas import (
    UserSettingsUpdate, UserSettingsResponse,
    TenantSettingsUpdate, TenantSettingsResponse,
    AIModelSettingsUpdate, AIModelSettingsResponse,
    SecuritySettingsUpdate, SecuritySettingsResponse
)


class SettingsService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ============== USER SETTINGS ==============
    
    async def get_user_settings(self, user_id: str) -> Optional[UserSettingsResponse]:
        """Get user settings"""
        result = await self.db.execute(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        settings = result.scalar_one_or_none()
        
        if not settings:
            # Create default settings
            settings = UserSettings(user_id=user_id)
            self.db.add(settings)
            await self.db.commit()
            await self.db.refresh(settings)
        
        return UserSettingsResponse.model_validate(settings)
    
    async def update_user_settings(self, user_id: str, data: UserSettingsUpdate) -> UserSettingsResponse:
        """Update user settings"""
        result = await self.db.execute(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        settings = result.scalar_one_or_none()
        
        if not settings:
            settings = UserSettings(user_id=user_id)
            self.db.add(settings)
        
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(settings, field, value)
        
        await self.db.commit()
        await self.db.refresh(settings)
        
        return UserSettingsResponse.model_validate(settings)
    
    # ============== TENANT SETTINGS ==============
    
    async def get_tenant_settings(self, tenant_id: str) -> Optional[TenantSettingsResponse]:
        """Get tenant settings"""
        result = await self.db.execute(
            select(TenantSettings).where(TenantSettings.tenant_id == tenant_id)
        )
        settings = result.scalar_one_or_none()
        
        if not settings:
            settings = TenantSettings(tenant_id=tenant_id)
            self.db.add(settings)
            await self.db.commit()
            await self.db.refresh(settings)
        
        return TenantSettingsResponse.model_validate(settings)
    
    async def update_tenant_settings(self, tenant_id: str, data: TenantSettingsUpdate) -> TenantSettingsResponse:
        """Update tenant settings"""
        result = await self.db.execute(
            select(TenantSettings).where(TenantSettings.tenant_id == tenant_id)
        )
        settings = result.scalar_one_or_none()
        
        if not settings:
            settings = TenantSettings(tenant_id=tenant_id)
            self.db.add(settings)
        
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(settings, field, value)
        
        await self.db.commit()
        await self.db.refresh(settings)
        
        return TenantSettingsResponse.model_validate(settings)
    
    # ============== AI MODEL SETTINGS ==============
    
    async def get_ai_settings(self, tenant_id: str) -> Optional[AIModelSettingsResponse]:
        """Get AI model settings"""
        result = await self.db.execute(
            select(AIModelSettings).where(AIModelSettings.tenant_id == tenant_id)
        )
        settings = result.scalar_one_or_none()
        
        if not settings:
            settings = AIModelSettings(tenant_id=tenant_id)
            self.db.add(settings)
            await self.db.commit()
            await self.db.refresh(settings)
        
        return AIModelSettingsResponse.model_validate(settings)
    
    async def update_ai_settings(self, tenant_id: str, data: AIModelSettingsUpdate) -> AIModelSettingsResponse:
        """Update AI model settings"""
        result = await self.db.execute(
            select(AIModelSettings).where(AIModelSettings.tenant_id == tenant_id)
        )
        settings = result.scalar_one_or_none()
        
        if not settings:
            settings = AIModelSettings(tenant_id=tenant_id)
            self.db.add(settings)
        
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(settings, field, value)
        
        await self.db.commit()
        await self.db.refresh(settings)
        
        return AIModelSettingsResponse.model_validate(settings)
    
    async def get_available_models(self) -> Dict[str, Any]:
        """Get available AI models"""
        return {
            "chat": [
                {"id": "gpt-4o", "name": "GPT-4o", "provider": "openai", "type": "primary"},
                {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "provider": "openai", "type": "fast"},
                {"id": "claude-sonnet-4-5-20250929", "name": "Claude Sonnet", "provider": "anthropic", "type": "primary"},
                {"id": "gemini-2.5-pro", "name": "Gemini Pro", "provider": "gemini", "type": "primary"}
            ],
            "vision": [
                {"id": "gpt-4o", "name": "GPT-4o Vision", "provider": "openai"}
            ],
            "voice": [
                {"id": "whisper-1", "name": "Whisper", "provider": "openai"}
            ],
            "tts": [
                {"id": "tts-1", "name": "TTS Standard", "provider": "openai"},
                {"id": "tts-1-hd", "name": "TTS HD", "provider": "openai"}
            ],
            "image": [
                {"id": "gpt-image-1", "name": "GPT Image", "provider": "openai"},
                {"id": "dall-e-3", "name": "DALL-E 3", "provider": "openai"}
            ],
            "voices": [
                {"id": "alloy", "name": "Alloy"},
                {"id": "echo", "name": "Echo"},
                {"id": "fable", "name": "Fable"},
                {"id": "nova", "name": "Nova"},
                {"id": "onyx", "name": "Onyx"},
                {"id": "shimmer", "name": "Shimmer"}
            ]
        }
    
    # ============== SECURITY SETTINGS ==============
    
    async def get_security_settings(self, tenant_id: str) -> Optional[SecuritySettingsResponse]:
        """Get security settings"""
        result = await self.db.execute(
            select(SecuritySettings).where(SecuritySettings.tenant_id == tenant_id)
        )
        settings = result.scalar_one_or_none()
        
        if not settings:
            settings = SecuritySettings(tenant_id=tenant_id)
            self.db.add(settings)
            await self.db.commit()
            await self.db.refresh(settings)
        
        return SecuritySettingsResponse.model_validate(settings)
    
    async def update_security_settings(self, tenant_id: str, data: SecuritySettingsUpdate) -> SecuritySettingsResponse:
        """Update security settings"""
        result = await self.db.execute(
            select(SecuritySettings).where(SecuritySettings.tenant_id == tenant_id)
        )
        settings = result.scalar_one_or_none()
        
        if not settings:
            settings = SecuritySettings(tenant_id=tenant_id)
            self.db.add(settings)
        
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(settings, field, value)
        
        await self.db.commit()
        await self.db.refresh(settings)
        
        return SecuritySettingsResponse.model_validate(settings)
    
    # ============== COMPANY SETTINGS ==============
    
    async def get_company_settings(self, tenant_id: str) -> Dict[str, Any]:
        """Get company/branding settings"""
        result = await self.db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            return {}
        
        return {
            "name": tenant.name,
            "slug": tenant.slug,
            "logo_url": tenant.logo_url,
            "domain": tenant.domain,
            "slogan": tenant.slogan,
            "brand_primary": tenant.brand_primary,
            "brand_secondary": tenant.brand_secondary,
            "ai_name": tenant.ai_name,
            "ai_persona": tenant.ai_persona
        }
    
    async def update_company_settings(self, tenant_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update company/branding settings"""
        result = await self.db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            return {}
        
        allowed_fields = ["name", "logo_url", "domain", "slogan", "brand_primary", "brand_secondary", "ai_name", "ai_persona"]
        for field, value in data.items():
            if field in allowed_fields:
                setattr(tenant, field, value)
        
        await self.db.commit()
        
        return await self.get_company_settings(tenant_id)
