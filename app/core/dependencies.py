from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from app.core.jwt import verify_token
from app.db.session import get_session
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/users/token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_session)],
) -> User:
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username: str = payload.get("sub")
    email: str = payload.get("email")
    user: User = session.exec(
        select(User).where(User.name == username and User.email == email)
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
