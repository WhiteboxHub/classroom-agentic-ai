import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from core.logging import get_logger
from core.config import Config

load_dotenv()
logger = get_logger(__name__, log_file="logs/app.log")

DATABASE_URL = Config.DATABASE_URL
if not DATABASE_URL:
    logger.error("DATABASE_URL is missing")
    raise ValueError("DATABASE_URL is missing")


try:
    engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
    logger.info("PostgreSQL engine created")
except Exception as e:
    logger.exception(f"Failed to create PostgreSQL engine: {e}")
    raise


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = None
    try:
        db = SessionLocal()
        return db
    except SQLAlchemyError as e:
        logger.exception(f"Database session error: {e}")
        raise
    # finally:
    #     if db:
    #         db.close()
