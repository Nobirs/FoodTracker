from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, Field, SQLModel


class AuditLogBase(SQLModel):
    action: str
    object_type: Optional[str] = None
    object_id: Optional[int] = None
    payload: Optional[dict] = Field(sa_column=Column(JSONB), default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuditLog(AuditLogBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)


class AuditLogRead(AuditLogBase):
    id: int


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogUpdate(SQLModel):
    action: Optional[str] = None
