from typing import Annotated

from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.config import settings
from app.core.dependencies import get_current_user
from app.core.jwt import create_access_token, create_refresh_token, verify_token
from app.core.redis import get_redis_client
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
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis_client)],
):
    username = form_data.username
    stmt = select(User).where(User.name == username)
    user = session.exec(stmt).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    access_token = create_access_token(data={"sub": user.name, "email": user.email})
    refresh_token, jti = create_refresh_token(
        data={"sub": user.name, "username": user.name, "email": user.email}
    )
    ttl = settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60
    await redis.set(f"refresh:{jti}", str(user.id), ex=ttl)
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/api/v1/users/refresh",
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    redis: Annotated[Redis, Depends(get_redis_client)],
):
    token = request.cookies.get("refresh_token")
    if token:
        payload = verify_token(token)
        jti = payload["jti"]
        if jti:
            await redis.delete(f"refresh:{jti}")
    response.delete_cookie("refresh_token", path="/api/v1/users/refresh")
    return {"msg": "logged out"}


@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    redis: Annotated[Redis, Depends(get_redis_client)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token"
        )
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    # check in redis
    jti = payload["jti"]
    user_id = await redis.get(f"refresh:{jti}")
    if not user_id or user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    await redis.delete(f"refresh:{jti}")

    # create new tokens
    refresh_token, jti = create_refresh_token(
        data={
            "sub": current_user.name,
            "username": current_user.name,
            "email": current_user.email,
        }
    )
    ttl = settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60
    await redis.set(f"refresh:{jti}", str(current_user.id), ex=ttl)
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/api/v1/users/refresh",
    )
    access_token = create_access_token(
        data={"sub": current_user.name, "email": current_user.email}
    )

    return Token(access_token=access_token, token_type="bearer")
