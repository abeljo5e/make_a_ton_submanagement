import hashlib
import re
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Union
import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User, UserRole

# Use standard HTTPBearer for OpenAPI docs and token parsing
http_bearer = HTTPBearer(auto_error=False)


# --- Password Hashing ---
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), 
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """Validate password complexity requirements."""
    if len(password) <= 8:
        return False, "Password must be longer than 8 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must include at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must include at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must include at least one numeric digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>\-_=+[\]/`~;\\]", password):
        return False, "Password must include at least one special character."
    return True, None


# --- JWT Tokens ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


# --- Dependencies ---
def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer), 
    db: Session = Depends(get_db)
) -> User:
    """FastAPI dependency to retrieve authenticated user from bearer token."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload: missing subject.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_uuid = uuid.UUID(str(user_id_str))
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identifier format.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with this token does not exist.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account. Please contact an administrator.",
        )
    return current_user


def require_role(allowed_roles: List[Union[UserRole, str]]):
    """Factory dependency for role-based access control."""
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        user_role_val = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
        allowed_str_roles = [
            r.value if hasattr(r, "value") else str(r) for r in allowed_roles
        ]
        if user_role_val not in allowed_str_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required roles: {allowed_str_roles}",
            )
        return current_user
    return role_checker


# Role helper dependencies
require_admin = require_role([UserRole.ADMIN, "admin"])
require_staff = require_role([UserRole.ADMIN, UserRole.STAFF, "admin", "staff"])
require_customer = require_role([UserRole.CUSTOMER, "customer"])
