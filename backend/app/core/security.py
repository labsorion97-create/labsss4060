"""
ORIONIS Security Utilities
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets
import pyotp
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token scheme
security = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh", "jti": secrets.token_urlsafe(32)})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """Decode a JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )


def generate_api_key() -> str:
    """Generate a secure API key"""
    return f"orionis_{secrets.token_urlsafe(32)}"


def generate_2fa_secret() -> str:
    """Generate a 2FA secret"""
    return pyotp.random_base32()


def verify_2fa_code(secret: str, code: str) -> bool:
    """Verify a 2FA code"""
    totp = pyotp.TOTP(secret)
    return totp.verify(code)


def get_2fa_uri(secret: str, email: str) -> str:
    """Get 2FA provisioning URI"""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name="ORIONIS")


async def get_current_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    request: Request = None
) -> Optional[str]:
    """Extract token from Authorization header or cookie"""
    # Try Authorization header first
    if credentials:
        return credentials.credentials
    
    # Try cookie
    if request:
        token = request.cookies.get("session_token")
        if token:
            return token
    
    return None
