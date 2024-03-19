import os

from typing import Optional
from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    app_title: str = 'Благотворительный фонд'
    description: str = 'Сервис по сбору пожертвований'
    database_url: str = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./fastapi.db')
    secret: str = 'SECRET'
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None

    class Config:
        env_file = '.env'


settings = Settings()
