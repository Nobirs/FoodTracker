from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.dependencies import get_current_user
from app.core.jwt import create_access_token, create_refresh_token
from app.core.security import get_password_hash, verify_password
from app.db.session import get_session
from app.models.user import Token, User, UserCreate, UserRead

router = APIRouter(prefix="/users")


@router.get("/all", response_model=list[UserRead])
async def get_users(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    statement = select(User)
    return session.exec(statement).all()


@router.post("/register", response_model=UserRead)
async def register(user: UserCreate, session: Annotated[Session, Depends(get_session)]):
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


@router.post("/token", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)],
):
    username = form_data.username
    stmt = select(User).where(User.name == username)
    user = session.exec(stmt).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    access_token = create_access_token(data={"sub": user.name, "email": user.email})
    refresh_token = create_refresh_token(
        data={"sub": user.name, "username": user.name, "email": user.email}
    )
    return Token(
        access_token=access_token, token_type="bearer", refresh_token=refresh_token
    )
