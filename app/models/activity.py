from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class ActivityBase(SQLModel):
    type: str
    duration_min: int = Field(default=0, ge=0)
    calories_burned: float | None = Field(default=None, nullable=True, ge=0)
    performed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Activity(ActivityBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)


class ActivityRead(ActivityBase):
    id: int


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(SQLModel):
    type: Optional[str] = None
    duration_min: int = Field(default=0, ge=0)
    calories_burned: float | None = Field(default=None, nullable=True, ge=0)
    performed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
