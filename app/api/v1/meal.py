import uuid
from datetime import timedelta
from io import BytesIO
from typing import Annotated, Optional

import requests  # type: ignore
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from app.core.background_tasks import BGAction, add_audit
from app.core.dependencies import get_current_user
from app.core.minio import BUCKET_NAME, minio_client
from app.db.session import get_session
from app.models.audit import AuditLogCreate
from app.models.meal import Meal
from app.models.user import User

router = APIRouter(prefix="/meal")


@router.get("/all", response_model=list[Meal])
async def get_meals(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    stmt = select(Meal).where(Meal.user_id == current_user.id)
    return session.exec(stmt).all()


@router.get("/{meal_id}", response_model=Meal)
async def get_meal(
    meal_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    db_meal = session.get(Meal, meal_id)
    if not db_meal or db_meal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Meal not found"
        )
    return db_meal


@router.post("/add", response_model=Meal)
async def add_meal(
    image: UploadFile,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    background_tasks: BackgroundTasks,
    name: str = Form(),
    notes: str = Form(),
    items: Optional[str] = Form(),
):
    if image:
        image_url = f"{uuid.uuid4().hex}_{image.filename}"
        await image.seek(0)
        minio_client.put_object(
            bucket_name=BUCKET_NAME,
            object_name=image_url,
            data=image.file,
            length=image.size,
            content_type=image.content_type,
        )
    new_meal = Meal(
        user_id=current_user.id, name=name, notes=notes, image_url=image_url
    )
    session.add(new_meal)
    session.commit()
    session.refresh(new_meal)
    background_tasks.add_task(
        add_audit,
        new_audit=AuditLogCreate(
            action=BGAction.ADD,
            object_type="meal",
            object_id=new_meal.id,
            payload=new_meal.model_dump(),
        ),
        user_id=current_user.id,
        session=session,
    )
    return new_meal


@router.get("/{meal_id}/image")
async def get_meal_image(
    meal_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    db_meal = session.get(Meal, meal_id)
    if not db_meal or db_meal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Meal not found"
        )
    if db_meal.image_url:
        url = minio_client.presigned_get_object(
            bucket_name=BUCKET_NAME,
            object_name=db_meal.image_url,
            expires=timedelta(days=1),
        )
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            return StreamingResponse(
                BytesIO(response.content),
                media_type=response.headers["Content-Type"],
                headers={
                    "Content-Disposition": f'inline; filename="{db_meal.image_url}"'
                },
            )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Could not retrieve image from MinIO",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Image url in database"
        )
