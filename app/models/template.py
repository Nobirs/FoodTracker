from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, Field, SQLModel


class Template(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    name: str
    items: Optional[list] = Field(sa_column=Column(JSONB), default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
