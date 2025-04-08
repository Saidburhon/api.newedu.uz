import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # API details
    API_V1_STR: str = "/v1"
    PROJECT_NAME: str = "NewEdu API"
    PROJECT_DESCRIPTION: str = "API for NewEdu platform where Uzbek youth can get high-tier education"
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "postgresql://postgres:password@localhost/newedu")
    
    # Security
    SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", "your-secret-key-for-dev-only")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 14  # 14 days
    
    # CORS
    ALLOWED_ORIGINS: list = ["*"]

settings = Settings()
