from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class Activity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    type: str
    duration_min: Optional[int] = None
    calories_burned: Optional[float] = None
    performed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
