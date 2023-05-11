from fastapi import Request
from functools import lru_cache

from app.config import Settings


@lru_cache()
def get_settings():
    settings = Settings()
    settings.DATABASE_URL = settings.DATABASE_URL.replace("postgres://", "postgresql://")
    return settings


def get_db(request: Request):
    return request.state.db
