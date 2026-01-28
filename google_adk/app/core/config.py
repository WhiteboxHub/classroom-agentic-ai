import os
from dotenv import load_dotenv
from core.logging import get_logger

logger = get_logger(__name__, log_file="logs/app.log")

# Load .env one time globally
load_dotenv()

class Config:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    GOOGLE_API_KEY : str = os.getenv("GOOGLE_API_KEY","")
    @staticmethod
    def validate():
        if not Config.DATABASE_URL:
            logger.error("DATABASE_URL is missing in .env")
            raise ValueError("DATABASE_URL is missing in .env")


Config.validate()
