from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(dotenv_path=BASE_DIR / ".env")


class Settings:
    def __init__(self):
        self.ACCESS_TOKEN_EXP = 15  # minutes
        self.REFRESH_TOKEN_EXP = 30  # days
        # openssl rand -hex 32
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        self.ALGORITHM = os.getenv("ALGORITHM")
        self.DB = {"DATABASE_URL": "sqlite:///./db.sqlite3"}


@lru_cache()
def get_settings():
    return Settings()
