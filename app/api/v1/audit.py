from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.dependencies import get_current_user
from app.db.session import get_session
from app.models.audit import AuditLog, AuditLogCreate, AuditLogRead
from app.models.user import User

router = APIRouter(prefix="/audit")


@router.get("/all", response_model=list[AuditLogRead])
async def get_all(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    stmt = select(AuditLog).where(AuditLog.user_id == current_user.id)
    return session.exec(stmt).all()


@router.get("/{audit_id}", response_model=AuditLogRead)
async def get_audit(
    audit_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    db_audit = session.get(AuditLog, audit_id)
    if not db_audit or db_audit.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Audit not found"
        )
    return db_audit


@router.post("/add", response_model=AuditLogRead)
async def add_audit(
    new_audit: AuditLogCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    audit = AuditLog(user_id=current_user.id, **new_audit.model_dump())
    session.add(audit)
    session.commit()
    session.refresh(audit)
    return audit
