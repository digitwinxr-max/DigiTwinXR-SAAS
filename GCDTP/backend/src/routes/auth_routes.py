"""
Authentication Routes

Provides JWT authentication endpoints:
- POST /auth/login - Login and get access/refresh tokens
- POST /auth/refresh - Refresh access token using refresh token
- POST /auth/logout - Revoke refresh token
"""
from datetime import datetime, timezone
from typing import Optional, Set
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel

from ..core.security import get_security_config


router = APIRouter(prefix="/auth", tags=["authentication"])

# In-memory refresh token storage (use Redis in production)
# Maps token_id -> token data
_revoked_tokens: Set[str] = set()
_refresh_token_store: dict = {}


class TokenResponse(BaseModel):
    """Response model for token endpoints."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Request model for token refresh."""
    refresh_token: str


class AccessTokenResponse(BaseModel):
    """Response model for access token only."""
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    """Response model for logout."""
    message: str


class TokenPayload(BaseModel):
    """JWT token payload."""
    sub: str  # user_id
    type: str  # token type (access or refresh)
    jti: str  # unique token id
    exp: datetime
    iat: datetime


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


def create_access_token(user_id: str) -> tuple[str, str]:
    """
    Create an access token for a user.
    
    Returns:
        Tuple of (token, token_id)
    """
    config = get_security_config()
    now = datetime.now(timezone.utc)
    token_id = str(uuid4())
    
    payload = {
        "sub": user_id,
        "type": config.ACCESS_TOKEN_TYPE,
        "jti": token_id,
        "exp": now + config.get_access_token_expire_timedelta(),
        "iat": now,
    }
    
    token = jwt.encode(
        payload,
        config.jwt_secret_key,
        algorithm=config.ALGORITHM
    )
    
    return token, token_id


def create_refresh_token(user_id: str) -> tuple[str, str]:
    """
    Create a refresh token for a user.
    
    Returns:
        Tuple of (token, token_id)
    """
    config = get_security_config()
    now = datetime.now(timezone.utc)
    token_id = str(uuid4())
    
    payload = {
        "sub": user_id,
        "type": config.REFRESH_TOKEN_TYPE,
        "jti": token_id,
        "exp": now + config.get_refresh_token_expire_timedelta(),
        "iat": now,
    }
    
    token = jwt.encode(
        payload,
        config.jwt_refresh_secret_key,
        algorithm=config.ALGORITHM
    )
    
    # Store token metadata for validation
    _refresh_token_store[token_id] = {
        "user_id": user_id,
        "created_at": now,
    }
    
    return token, token_id


def validate_refresh_token(token: str) -> Optional[TokenPayload]:
    """
    Validate a refresh token.
    
    Returns:
        TokenPayload if valid, None otherwise
    """
    config = get_security_config()
    
    try:
        payload = jwt.decode(
            token,
            config.jwt_refresh_secret_key,
            algorithms=[config.ALGORITHM]
        )
        
        # Check token type
        if payload.get("type") != config.REFRESH_TOKEN_TYPE:
            return None
        
        # Check if token is revoked
        token_id = payload.get("jti")
        if token_id in _revoked_tokens:
            return None
        
        # Check if token exists in store
        if token_id not in _refresh_token_store:
            return None
        
        return TokenPayload(
            sub=payload["sub"],
            type=payload["type"],
            jti=token_id,
            exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
            iat=datetime.fromtimestamp(payload["iat"], tz=timezone.utc),
        )
        
    except JWTError:
        return None


def validate_access_token(token: str) -> Optional[TokenPayload]:
    """
    Validate an access token.
    
    Returns:
        TokenPayload if valid, None otherwise
    """
    config = get_security_config()
    
    try:
        payload = jwt.decode(
            token,
            config.jwt_secret_key,
            algorithms=[config.ALGORITHM]
        )
        
        # Check token type
        if payload.get("type") != config.ACCESS_TOKEN_TYPE:
            return None
        
        return TokenPayload(
            sub=payload["sub"],
            type=payload["type"],
            jti=payload.get("jti", ""),
            exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
            iat=datetime.fromtimestamp(payload["iat"], tz=timezone.utc),
        )
        
    except JWTError:
        return None


def revoke_refresh_token(token: str) -> bool:
    """
    Revoke a refresh token.
    
    Returns:
        True if revoked, False if token was invalid
    """
    payload = validate_refresh_token(token)
    if payload:
        _revoked_tokens.add(payload.jti)
        # Remove from store
        if payload.jti in _refresh_token_store:
            del _refresh_token_store[payload.jti]
        return True
    return False


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Optional[str]:
    """
    Dependency to get current user from access token.
    
    Returns:
        User ID if valid token, None otherwise
    """
    if not token:
        return None
    
    payload = validate_access_token(token)
    if payload:
        return payload.sub
    return None


async def get_required_user(token: str = Depends(oauth2_scheme)) -> str:
    """
    Dependency to get current user, raising exception if not authenticated.
    
    Returns:
        User ID
        
    Raises:
        HTTPException: If no valid token
    """
    user_id = await get_current_user(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id


# Demo user for testing (in production, validate against database)
DEMO_USERS = {
    "admin": {"password": "admin123", "user_id": "user-001"},
    "testuser": {"password": "test123", "user_id": "user-002"},
}


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login endpoint.
    
    Authenticates user and returns access and refresh tokens.
    
    Demo credentials:
        - admin / admin123
        - testuser / test123
    """
    # Validate credentials (demo implementation)
    user = DEMO_USERS.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = user["user_id"]
    
    # Generate tokens
    access_token, _ = create_access_token(user_id)
    refresh_token, _ = create_refresh_token(user_id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh_token(request: RefreshRequest):
    """
    Refresh access token using refresh token.
    
    Validates the refresh token and issues a new access token.
    """
    payload = validate_refresh_token(request.refresh_token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate new access token
    user_id = payload.sub
    access_token, _ = create_access_token(user_id)
    
    return AccessTokenResponse(
        access_token=access_token,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(request: RefreshRequest):
    """
    Logout endpoint.
    
    Revokes the refresh token.
    After logout, the refresh token will no longer work.
    """
    revoked = revoke_refresh_token(request.refresh_token)
    
    if revoked:
        return MessageResponse(message="Successfully logged out")
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


@router.get("/me")
async def get_me(user_id: str = Depends(get_required_user)):
    """
    Get current user info.
    
    Requires valid access token.
    """
    return {
        "user_id": user_id,
        "status": "active",
    }