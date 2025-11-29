from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os
import secrets

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Project Configuration
    project_id: str = "research-buddy-local"
    environment: str = "development"

    # API Configuration
    api_v1_prefix: str = "/api/v1"

    # Google Cloud Configuration
    google_application_credentials: Optional[str] = None
    vertex_ai_location: str = "us-central1"
    vertex_ai_api_key: Optional[str] = None
    gcs_bucket_name: str = "research-papers-bucket"

    # Firebase Configuration
    firebase_admin_sdk_path: Optional[str] = None

    # External APIs
    serp_api_key: Optional[str] = None
    ieee_api_key: Optional[str] = None

    # Security Configuration
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Database Configuration (if needed in future)
    database_url: Optional[str] = None

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # Logging Configuration
    log_level: str = "INFO"

    # CORS Configuration
    allowed_origins: str = "http://localhost:3000,http://localhost:8080"
    
    # Pydantic v2 settings config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields from env
    )
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment.lower() == "production"
    
    @property
    def allowed_origins_list(self) -> list[str]:
        """Convert allowed origins string to list"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

# Create settings instance
settings = Settings()