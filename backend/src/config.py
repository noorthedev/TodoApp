"""Application configuration using pydantic-settings."""
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str

    @field_validator('DATABASE_URL')
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate DATABASE_URL format for async SQLAlchemy with asyncpg."""
        if not v:
            raise ValueError("DATABASE_URL cannot be empty")

        # Check for common mistakes
        if v.startswith("psql "):
            raise ValueError("DATABASE_URL should not start with 'psql' command")
        if "'" in v or '"' in v:
            raise ValueError("DATABASE_URL should not contain quotes")
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "DATABASE_URL must use 'postgresql+asyncpg://' scheme for async connections. "
                f"Got: {v.split('://')[0] if '://' in v else 'no scheme'}"
            )
        if "sslmode=" in v:
            raise ValueError(
                "Use 'ssl=require' instead of 'sslmode=require' for asyncpg driver"
            )
        if "channel_binding=" in v:
            raise ValueError(
                "asyncpg does not support 'channel_binding' parameter. Remove it from DATABASE_URL"
            )

        return v
    
    # JWT Configuration
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:3000"
    
    # Application
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
