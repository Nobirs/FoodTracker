from datetime import datetime, timezone
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Column, Field, SQLModel, String


class UserBase(SQLModel):
    email: EmailStr = Field(index=True, unique=True)
    name: Optional[str] = None
    timezone: Optional[str] = "UTC"


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field(sa_column=Column(String, nullable=False))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    created_at: datetime


class UserUpdate(SQLModel):
    name: Optional[str]
    timezone: Optional[str]


class Token(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(SQLModel):
    username: Optional[str] = None
    email: Optional[str] = None
