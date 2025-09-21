"""API Configuration"""
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Application
    app_name: str = "AgentZero API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./agentzero.db")

    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 100

    # WebSocket
    ws_heartbeat_interval: int = 30  # seconds
    ws_max_connections: int = 1000

    # Hive Configuration
    max_agents: int = 100
    max_tasks_per_agent: int = 10
    task_timeout: int = 3600  # seconds

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()