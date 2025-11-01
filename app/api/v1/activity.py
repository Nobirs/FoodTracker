from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.background_tasks import BGAction, add_audit
from app.core.dependencies import get_current_user
from app.db.session import get_session
from app.models.activity import Activity, ActivityCreate, ActivityRead, ActivityUpdate
from app.models.audit import AuditLogCreate
from app.models.user import User

router = APIRouter(prefix="/activity")


@router.get("/all", response_model=list[ActivityRead])
async def get_all(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    stmt = select(Activity).where(Activity.user_id == current_user.id)
    return session.exec(stmt).all()


@router.get("/{activity_id}", response_model=ActivityRead)
async def get_activity(
    activity_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    db_activity = session.get(Activity, activity_id)
    if not db_activity or db_activity.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found"
        )
    return db_activity


@router.post("/add", response_model=ActivityRead)
async def add_activity(
    new_activity: ActivityCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    background_tasks: BackgroundTasks,
):
    activity = Activity(user_id=current_user.id, **new_activity.model_dump())
    session.add(activity)
    session.commit()
    session.refresh(activity)
    background_tasks.add_task(
        add_audit,
        new_audit=AuditLogCreate(
            action=BGAction.ADD,
            object_type="activity",
            object_id=activity.id,
            payload=activity.model_dump(),
        ),
        user_id=current_user.id,
        session=session,
    )
    return activity


@router.patch("/update/{activity_id}", response_model=ActivityRead)
async def udpate_activity(
    activity_id: int,
    updated_activity: ActivityUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    background_tasks: BackgroundTasks,
):
    db_activity = session.get(Activity, activity_id)
    if not db_activity or db_activity.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found"
        )
    updated_data = updated_activity.model_dump(exclude_unset=True)
    db_activity.sqlmodel_update(updated_data)
    session.add(db_activity)
    session.commit()
    session.refresh(db_activity)
    background_tasks.add_task(
        add_audit,
        new_audit=AuditLogCreate(
            action=BGAction.UPDATE,
            object_type="activity",
            object_id=activity_id,
            payload=db_activity.model_dump(),
        ),
        user_id=current_user.id,
        session=session,
    )
    return db_activity


@router.delete("/delete/{activity_id}")
async def delete_activity(
    activity_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    background_tasks: BackgroundTasks,
):
    db_activity = session.get(Activity, activity_id)
    if not db_activity or db_activity.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found"
        )
    session.delete(db_activity)
    session.commit()
    background_tasks.add_task(
        add_audit,
        new_audit=AuditLogCreate(
            action=BGAction.DELETE,
            object_type="activity",
            object_id=activity_id,
            payload=db_activity.model_dump(),
        ),
        user_id=current_user.id,
        session=session,
    )
    return {"msg": "Activity deleted"}
