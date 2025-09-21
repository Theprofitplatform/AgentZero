"""Authentication Models"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"

class LoginRequest(BaseModel):
    """Login request model"""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")

class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str = Field(..., description="Access token")
    refresh_token: Optional[str] = Field(None, description="Refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")

class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str = Field(..., description="Refresh token")

class User(BaseModel):
    """User model"""
    id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: Optional[EmailStr] = Field(None, description="Email address")
    role: UserRole = Field(UserRole.USER, description="User role")
    is_active: bool = Field(True, description="User active status")

class UserInDB(User):
    """User in database with hashed password"""
    hashed_password: str

class APIKey(BaseModel):
    """API Key model"""
    key: str = Field(..., description="API key")
    name: str = Field(..., description="Key name")
    user_id: str = Field(..., description="Owner user ID")
    created_at: str = Field(..., description="Creation timestamp")
    expires_at: Optional[str] = Field(None, description="Expiration timestamp")
    is_active: bool = Field(True, description="Key active status")