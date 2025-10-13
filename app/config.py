from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Food Tracker"
    DATABASE_URL: str = "postgresql+psycopg://postgres:password@db:5432/fooddb"
    REDIS_URL: str = "redis://redis:6379/0"
    SECRET_KEY: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
