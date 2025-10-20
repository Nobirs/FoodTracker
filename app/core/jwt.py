from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError

from app.config import settings


def create_jwt_token(data: dict, expires_delta: int) -> str:
    to_encode: dict = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    token: str = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return token


def create_access_token(data: dict) -> str:
    return create_jwt_token(data, settings.ACCESS_TOKEN_EXPIRE_MINUTES)


def create_refresh_token(data: dict) -> str:
    return create_jwt_token(data, settings.REFRESH_TOKEN_EXPIRE_MINUTES)


def verify_token(token: str):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except InvalidTokenError:
        return None
