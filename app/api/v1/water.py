from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.dependencies import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.models.water import WaterCreate, WaterIntake, WaterRead, WaterUpdate

router = APIRouter(prefix="/water")


@router.get("/all", response_model=list[WaterRead])
async def get_all(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    stmt = select(WaterIntake).where(WaterIntake.user_id == current_user.id)
    return session.exec(stmt).all()


@router.get("/{water_id}", response_model=WaterRead)
async def get_water(
    water_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    db_water = session.get(WaterIntake, water_id)
    if not db_water or db_water.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Water not found"
        )
    return db_water


@router.post("/add", response_model=WaterRead)
async def add_water(
    new_water: WaterCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    water = WaterIntake(user_id=current_user.id, **new_water.model_dump())
    session.add(water)
    session.commit()
    session.refresh(water)
    return water


@router.patch("/update/{water_id}", response_model=WaterRead)
async def update_water(
    water_id: int,
    update_water: WaterUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    db_water = session.get(WaterIntake, water_id)
    if not db_water or db_water.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Water not found"
        )
    update_data = update_water.model_dump(exclude_unset=True)
    db_water.sqlmodel_update(update_data)
    session.add(db_water)
    session.commit()
    session.refresh(db_water)
    return db_water


@router.delete("/delete/{water_id}")
async def delete_water(
    water_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    db_water = session.get(WaterIntake, water_id)
    if not db_water or db_water.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Water not found"
        )
    session.delete(db_water)
    session.commit()
    return {"msg": "Water deleted"}
