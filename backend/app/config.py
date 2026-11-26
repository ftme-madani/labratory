from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "سامانه آزمایشگاه مجازی هوشمند علوم تجربی"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    # Security & JWT
    SECRET_KEY: str = "dev-insecure-secret-key-change-in-production-1234567890"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database (SQLite by default, easily switched to PostgreSQL)
    DATABASE_URL: str = "sqlite:///./virtual_lab.db"

    # Optional Server-side LLM API Key (Never exposed to client)
    LLM_API_KEY: Optional[str] = None

    # Google Gemini AI Assistant Settings (Server-side only)
    GEMINI_API_KEY: Optional[str] = None
    AI_MODEL: str = "gemini-flash-lite-latest"
    AI_ENABLED: bool = True
    AI_TIMEOUT_SECONDS: float = 12.0
    AI_MAX_OUTPUT_TOKENS: int = 600
    AI_TEMPERATURE: float = 0.4

    model_config = SettingsConfigDict(env_file=[".env", "backend/.env"], case_sensitive=True, extra="ignore")

    @property
    def effective_gemini_api_key(self) -> Optional[str]:
        """بازگردانی کلید معتبر با اولویت GEMINI_API_KEY یا LLM_API_KEY"""
        key = self.GEMINI_API_KEY or self.LLM_API_KEY
        if key and key.strip() and not key.startswith("your-") and not key.startswith("replace_"):
            return key.strip()
        return None

settings = Settings()
