import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    MOCK_MODE: bool = os.getenv("MOCK_MODE", "True").lower() in ("true", "1", "yes")
    
    # Meta / Instagram Credentials
    INSTAGRAM_ACCOUNT_ID: str = os.getenv("INSTAGRAM_ACCOUNT_ID", "")
    INSTAGRAM_ACCESS_TOKEN: str = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    META_APP_SECRET: str = os.getenv("META_APP_SECRET", "")
    META_VERIFY_TOKEN: str = os.getenv("META_VERIFY_TOKEN", "insta_hub_secret_verify_token_2026")
    
    # Server & Media Settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    MEDIA_DIR: Path = BASE_DIR / "media"
    DB_PATH: Path = BASE_DIR / "insta_hub.db"
    ALLOWED_ORIGINS: list[str] = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")]

settings = Settings()

# Ensure media directory exists
settings.MEDIA_DIR.mkdir(parents=True, exist_ok=True)
