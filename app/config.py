from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Food Tracker"
    DATABASE_URL: str = "postgresql+psycopg://postgres:password@db:5432/fooddb"
    REDIS_URL: str = "redis://redis:6379/0"
    SECRET_KEY: str

    # jwt settings
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30 days in minutes

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
