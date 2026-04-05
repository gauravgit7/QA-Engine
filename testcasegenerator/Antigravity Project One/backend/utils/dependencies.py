from fastapi import Depends, Header
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from database.connection import get_db
from database.models import User
from config.settings import settings
from utils.exceptions import UnauthorizedException


async def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency that extracts the JWT from the Authorization header,
    validates it, and returns the corresponding User ORM object.
    """
    if not authorization:
        raise UnauthorizedException("Authorization header is missing")

    # Support both "Bearer <token>" and raw token
    token = authorization
    if authorization.lower().startswith("bearer "):
        token = authorization[7:]

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise UnauthorizedException("Token payload is invalid")
        user_id = int(user_id_str)
    except JWTError:
        raise UnauthorizedException("Token is invalid or expired")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise UnauthorizedException("User not found")

    return user
