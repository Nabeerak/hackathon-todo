"""Environment configuration using Pydantic settings."""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Find .env file at repository root (two levels up from this file)
ENV_FILE = Path(__file__).parent.parent.parent / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/todo_db"

    # JWT
    jwt_secret_key: str = "change-this-secret-key-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_days: int = 7

    # API
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"

    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:3001"

    # Environment
    environment: str = "development"

    # Phase 3: AI Configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_max_tokens: int = 200  # Reduced from 500 to control costs
    openai_temperature: float = 0.3

    # Phase 3: Rate Limiting (adjusted to meet <$0.15/user/month budget)
    ai_rate_limit_per_day: int = 15  # Reduced from 100 to meet cost target
    ai_rate_limit_per_hour: int = 5   # Reduced from 20 to meet cost target

    # Phase 3: Feature Flags
    ai_features_enabled: bool = True

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def allowed_origins_list(self) -> list[str]:
        """Convert comma-separated origins to list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


# Global settings instance
settings = Settings()
