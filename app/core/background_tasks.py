from datetime import datetime
from enum import StrEnum

from sqlmodel import Session

from app.models.audit import AuditLog, AuditLogCreate


class BGAction(StrEnum):
    USER = "USER"
    ADD = "ADD"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


async def add_audit(
    new_audit: AuditLogCreate, session: Session, user_id: int | None = None
) -> None:
    audit = AuditLog(user_id=user_id, **new_audit.model_dump())
    if audit.payload:
        for key, value in audit.payload.items():
            if isinstance(value, datetime):
                audit.payload[key] = value.isoformat()
    session.add(audit)
    session.commit()
    return
