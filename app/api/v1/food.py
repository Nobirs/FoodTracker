from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.background_tasks import BGAction, add_audit
from app.core.dependencies import get_current_user
from app.core.utils import update_dict_recursive
from app.db.session import get_session
from app.models.audit import AuditLogCreate
from app.models.food import FoodCreate, FoodItem, FoodRead, FoodUpdate
from app.models.user import User

router = APIRouter(prefix="/food")


@router.get("/all", response_model=list[FoodRead])
async def get_all(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    stmt = select(FoodItem).where(FoodItem.created_by == current_user.id)
    return session.exec(stmt).all()


@router.get("/{food_id}", response_model=FoodRead)
async def get_food(
    food_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    db_food = session.get(FoodItem, food_id)
    if not db_food or db_food.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Food not found"
        )
    return db_food


@router.post("/add", response_model=FoodCreate)
async def add_food(
    new_food: FoodCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    background_tasks: BackgroundTasks,
):
    # TODO: analyze food by name and add/update carbs
    food = FoodItem(created_by=current_user.id, **new_food.model_dump())
    session.add(food)
    session.commit()
    session.refresh(food)
    background_tasks.add_task(
        add_audit,
        new_audit=AuditLogCreate(
            action=BGAction.ADD,
            object_type="food",
            object_id=food.id,
            payload=food.model_dump(),
        ),
        user_id=current_user.id,
        session=session,
    )
    return food


@router.patch("/update/{food_id}", response_model=FoodRead)
async def update_food(
    food_id: int,
    updated_food: FoodUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    background_tasks: BackgroundTasks,
):
    db_food = session.get(FoodItem, food_id)
    if not db_food or db_food.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Food not found"
        )
    update_data = updated_food.model_dump(exclude_unset=True)

    if db_food.nutrients and update_data.get("nutrients"):
        nutrients = db_food.model_dump()["nutrients"]
        update_dict_recursive(nutrients, update_data["nutrients"])
        update_data["nutrients"] = nutrients

    db_food.sqlmodel_update(update_data)
    session.add(db_food)
    session.commit()
    session.refresh(db_food)
    background_tasks.add_task(
        add_audit,
        new_audit=AuditLogCreate(
            action=BGAction.UPDATE,
            object_type="food",
            object_id=db_food.id,
            payload=db_food.model_dump(),
        ),
        user_id=current_user.id,
        session=session,
    )
    return db_food


@router.delete("/delete/{food_id}")
async def delete_food(
    food_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    background_tasks: BackgroundTasks,
):
    db_food = session.get(FoodItem, food_id)
    if not db_food or db_food.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Food not found"
        )
    session.delete(db_food)
    session.commit()
    background_tasks.add_task(
        add_audit,
        new_audit=AuditLogCreate(
            action=BGAction.DELETE,
            object_type="food",
            object_id=food_id,
            payload=db_food.model_dump(),
        ),
        user_id=current_user.id,
        session=session,
    )
    return {"msg": "Food deleted"}
