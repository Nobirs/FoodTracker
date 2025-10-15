from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.user import User, UserCreate, UserRead

router = APIRouter()


@router.get("/user", response_model=list[UserRead])
async def get_users(session: Annotated[Session, Depends(get_session)]):
    statement = select(User)
    return session.exec(statement).all()


@router.post("/user/new", response_model=UserRead)
async def create_user(
    user: UserCreate, session: Annotated[Session, Depends(get_session)]
):
    model_data = user.model_dump()
    pwd = model_data.pop("password")
    db_user = User(**model_data, hashed_password=pwd)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
