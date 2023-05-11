from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    secret: str
    vkkey: str

    class Config:
        env_file = ".env"
