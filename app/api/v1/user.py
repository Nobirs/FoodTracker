from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from sqlmodel import Session

from app.db.session import get_session
from app.models.user import User, UserCreate, UserRead

router = APIRouter()


@router.get("/user", response_model=list[UserRead])
async def get_users(session: Annotated[Session, Depends(get_session)]):
    return session.exec(User.select()).all()


@router.post("/user/new", response_model=UserRead)
async def create_user(
    user: UserCreate, session: Annotated[Session, Depends(get_session)]
):
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
