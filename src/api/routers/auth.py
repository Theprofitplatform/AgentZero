"""Authentication API Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta

from ..models.auth import LoginRequest, TokenResponse, RefreshTokenRequest, User
from ..services.auth import auth_service
from ..config import settings

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest) -> TokenResponse:
    """
    Authenticate user and return access tokens.

    Returns JWT access token and refresh token for API authentication.
    """
    user = await auth_service.authenticate_user(
        credentials.username,
        credentials.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )

    refresh_token = auth_service.create_refresh_token(
        data={"sub": user.username}
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest) -> TokenResponse:
    """
    Refresh access token using refresh token.

    Exchange a valid refresh token for a new access token.
    """
    try:
        payload = auth_service.decode_token(request.refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        username = payload.get("sub")
        user = await auth_service.get_user(username)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = auth_service.create_access_token(
            data={"sub": user.username, "role": user.role},
            expires_delta=access_token_expires
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=request.refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

@router.get("/me", response_model=User)
async def get_current_user(
    current_user: User = Depends(auth_service.get_current_user)
) -> User:
    """
    Get current authenticated user information.

    Returns the profile information of the currently authenticated user.
    """
    return current_user

@router.post("/logout")
async def logout(
    current_user: User = Depends(auth_service.get_current_user)
) -> dict:
    """
    Logout the current user.

    Invalidates the current session. Note: Client should also remove
    stored tokens.
    """
    # In a production system, you would add the token to a blacklist
    # or invalidate it in your session store
    return {"message": "Successfully logged out"}