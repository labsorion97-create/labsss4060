"""
ORIONIS Auth Service
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException, status
import secrets
import httpx

from app.models.models import User, UserSession, Tenant, Membership, Role, UserSettings, TenantSettings, AIModelSettings, SecuritySettings, BillingSettings, RoleType
from app.schemas.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse, UserWithTenant
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token, generate_2fa_secret, verify_2fa_code, get_2fa_uri
from app.core.config import settings


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def register(self, data: RegisterRequest) -> Tuple[User, Tenant]:
        """Register a new user and create their tenant"""
        # Check if user exists
        result = await self.db.execute(select(User).where(User.email == data.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user
        user = User(
            email=data.email,
            password_hash=get_password_hash(data.password),
            name=data.name,
            status="active"
        )
        self.db.add(user)
        await self.db.flush()
        
        # Create user settings
        user_settings = UserSettings(user_id=user.id)
        self.db.add(user_settings)
        
        # Create tenant
        tenant_name = data.tenant_name or f"{data.name}'s Organization"
        slug = tenant_name.lower().replace(" ", "-").replace("'", "")[:50]
        
        # Ensure unique slug
        base_slug = slug
        counter = 1
        while True:
            result = await self.db.execute(select(Tenant).where(Tenant.slug == slug))
            if not result.scalar_one_or_none():
                break
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        tenant = Tenant(name=tenant_name, slug=slug)
        self.db.add(tenant)
        await self.db.flush()
        
        # Create tenant settings
        tenant_settings = TenantSettings(tenant_id=tenant.id)
        ai_settings = AIModelSettings(tenant_id=tenant.id)
        security_settings = SecuritySettings(tenant_id=tenant.id)
        billing_settings = BillingSettings(tenant_id=tenant.id)
        
        self.db.add_all([tenant_settings, ai_settings, security_settings, billing_settings])
        
        # Get or create owner role
        result = await self.db.execute(select(Role).where(Role.type == RoleType.OWNER))
        role = result.scalar_one_or_none()
        if not role:
            role = Role(name="Owner", type=RoleType.OWNER, is_system=True)
            self.db.add(role)
            await self.db.flush()
        
        # Create membership
        membership = Membership(
            user_id=user.id,
            tenant_id=tenant.id,
            role_id=role.id,
            is_default=True
        )
        self.db.add(membership)
        
        await self.db.commit()
        return user, tenant
    
    async def login(self, data: LoginRequest) -> Tuple[User, Tenant, TokenResponse]:
        """Login a user and return tokens"""
        # Find user
        result = await self.db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()
        
        if not user or not user.password_hash:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not verify_password(data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if user.status != "active":
            raise HTTPException(status_code=403, detail="Account is not active")
        
        # Check 2FA
        if user.two_factor_enabled:
            if not data.two_factor_code:
                raise HTTPException(status_code=401, detail="2FA code required")
            if not verify_2fa_code(user.two_factor_secret, data.two_factor_code):
                raise HTTPException(status_code=401, detail="Invalid 2FA code")
        
        # Get default tenant
        result = await self.db.execute(
            select(Membership).where(
                and_(Membership.user_id == user.id, Membership.is_default == True)
            )
        )
        membership = result.scalar_one_or_none()
        
        if not membership:
            raise HTTPException(status_code=403, detail="No tenant access")
        
        result = await self.db.execute(select(Tenant).where(Tenant.id == membership.tenant_id))
        tenant = result.scalar_one_or_none()
        
        # Create tokens
        token_data = {
            "sub": user.id,
            "email": user.email,
            "tenant_id": tenant.id
        }
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Create session
        session = UserSession(
            user_id=user.id,
            session_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        self.db.add(session)
        
        # Update last login
        user.last_login_at = datetime.now(timezone.utc)
        
        await self.db.commit()
        
        return user, tenant, TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token"""
        payload = decode_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        # Find session
        result = await self.db.execute(
            select(UserSession).where(UserSession.refresh_token == refresh_token)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=401, detail="Session not found")
        
        if session.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Session expired")
        
        # Create new tokens
        token_data = {
            "sub": payload["sub"],
            "email": payload["email"],
            "tenant_id": payload["tenant_id"]
        }
        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)
        
        # Update session
        session.session_token = new_access_token
        session.refresh_token = new_refresh_token
        session.expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        await self.db.commit()
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def logout(self, token: str) -> bool:
        """Logout user by invalidating session"""
        result = await self.db.execute(
            select(UserSession).where(UserSession.session_token == token)
        )
        session = result.scalar_one_or_none()
        
        if session:
            await self.db.delete(session)
            await self.db.commit()
        
        return True
    
    async def get_current_user(self, token: str) -> UserWithTenant:
        """Get current user from token"""
        payload = decode_token(token)
        
        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Get tenant and role
        tenant = None
        role = None
        permissions = []
        
        if tenant_id:
            result = await self.db.execute(select(Tenant).where(Tenant.id == tenant_id))
            tenant = result.scalar_one_or_none()
            
            result = await self.db.execute(
                select(Membership).where(
                    and_(Membership.user_id == user_id, Membership.tenant_id == tenant_id)
                )
            )
            membership = result.scalar_one_or_none()
            
            if membership:
                result = await self.db.execute(select(Role).where(Role.id == membership.role_id))
                role_obj = result.scalar_one_or_none()
                if role_obj:
                    role = role_obj.name
        
        return UserWithTenant(
            id=user.id,
            email=user.email,
            name=user.name,
            avatar_url=user.avatar_url,
            language=user.language,
            timezone=user.timezone,
            status=user.status,
            is_verified=user.is_verified,
            two_factor_enabled=user.two_factor_enabled,
            created_at=user.created_at,
            updated_at=user.updated_at,
            current_tenant=tenant,
            role=role,
            permissions=permissions
        )
    
    async def oauth_exchange(self, session_id: str) -> Tuple[User, Tenant, TokenResponse]:
        """Exchange OAuth session for tokens"""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                    headers={"X-Session-ID": session_id},
                    timeout=10.0
                )
                if resp.status_code != 200:
                    raise HTTPException(status_code=401, detail="Invalid session")
                
                data = resp.json()
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Auth service unavailable")
        
        # Find or create user
        result = await self.db.execute(select(User).where(User.email == data["email"]))
        user = result.scalar_one_or_none()
        
        if user:
            # Update user info
            user.name = data["name"]
            user.avatar_url = data.get("picture")
            user.last_login_at = datetime.now(timezone.utc)
            
            # Get default tenant
            result = await self.db.execute(
                select(Membership).where(
                    and_(Membership.user_id == user.id, Membership.is_default == True)
                )
            )
            membership = result.scalar_one_or_none()
            
            if membership:
                result = await self.db.execute(select(Tenant).where(Tenant.id == membership.tenant_id))
                tenant = result.scalar_one()
            else:
                raise HTTPException(status_code=403, detail="No tenant access")
        else:
            # Create new user and tenant
            user = User(
                email=data["email"],
                name=data["name"],
                avatar_url=data.get("picture"),
                oauth_provider="google",
                oauth_id=data.get("id"),
                status="active",
                is_verified=True
            )
            self.db.add(user)
            await self.db.flush()
            
            # Create user settings
            user_settings = UserSettings(user_id=user.id)
            self.db.add(user_settings)
            
            # Create tenant
            tenant_name = f"{data['name']}'s Organization"
            slug = data["email"].split("@")[0].lower()[:50]
            
            tenant = Tenant(name=tenant_name, slug=slug)
            self.db.add(tenant)
            await self.db.flush()
            
            # Create tenant settings
            self.db.add_all([
                TenantSettings(tenant_id=tenant.id),
                AIModelSettings(tenant_id=tenant.id),
                SecuritySettings(tenant_id=tenant.id),
                BillingSettings(tenant_id=tenant.id)
            ])
            
            # Get or create owner role
            result = await self.db.execute(select(Role).where(Role.type == RoleType.OWNER))
            role = result.scalar_one_or_none()
            if not role:
                role = Role(name="Owner", type=RoleType.OWNER, is_system=True)
                self.db.add(role)
                await self.db.flush()
            
            # Create membership
            membership = Membership(
                user_id=user.id,
                tenant_id=tenant.id,
                role_id=role.id,
                is_default=True
            )
            self.db.add(membership)
        
        # Create tokens
        token_data = {
            "sub": user.id,
            "email": user.email,
            "tenant_id": tenant.id
        }
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Create session
        session = UserSession(
            user_id=user.id,
            session_token=data.get("session_token", access_token),
            refresh_token=refresh_token,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        self.db.add(session)
        
        await self.db.commit()
        
        return user, tenant, TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def enable_2fa(self, user_id: str) -> Tuple[str, str]:
        """Enable 2FA for user"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        secret = generate_2fa_secret()
        uri = get_2fa_uri(secret, user.email)
        
        user.two_factor_secret = secret
        await self.db.commit()
        
        return secret, uri
    
    async def confirm_2fa(self, user_id: str, code: str) -> bool:
        """Confirm and enable 2FA"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user or not user.two_factor_secret:
            raise HTTPException(status_code=400, detail="2FA not initialized")
        
        if not verify_2fa_code(user.two_factor_secret, code):
            raise HTTPException(status_code=400, detail="Invalid code")
        
        user.two_factor_enabled = True
        await self.db.commit()
        
        return True
    
    async def disable_2fa(self, user_id: str, code: str) -> bool:
        """Disable 2FA"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user or not user.two_factor_enabled:
            raise HTTPException(status_code=400, detail="2FA not enabled")
        
        if not verify_2fa_code(user.two_factor_secret, code):
            raise HTTPException(status_code=400, detail="Invalid code")
        
        user.two_factor_enabled = False
        user.two_factor_secret = None
        await self.db.commit()
        
        return True
