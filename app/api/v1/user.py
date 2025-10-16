from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.security import get_password_hash
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
    # Pre-check: ensure email isn't already used
    statement = select(User).where(User.email == user.email)
    existing = session.exec(statement).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    model_data = user.model_dump()
    pwd = model_data.pop("password")
    hashed = get_password_hash(pwd)
    db_user = User(**model_data, hashed_password=hashed)
    session.add(db_user)
    try:
        session.commit()
    except IntegrityError:
        # Race condition: another request inserted same email concurrently
        session.rollback()
        raise HTTPException(status_code=409, detail="Email already registered")

    session.refresh(db_user)
    return db_user
