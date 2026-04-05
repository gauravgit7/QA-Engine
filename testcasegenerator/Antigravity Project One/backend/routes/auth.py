from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import User
from models.schemas import LoginRequest, RegisterRequest, TokenResponse, UserPublic
from services.auth_service import hash_password, verify_password, create_access_token
from utils.exceptions import UnauthorizedException, AppException

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate a user and return a JWT token."""
    # Allow login by email OR username
    user = db.query(User).filter(
        (User.email == request.email) | (User.username == request.email)
    ).first()

    if not user:
        raise UnauthorizedException("Invalid email or password")

    if not verify_password(request.password, user.password_hash):
        raise UnauthorizedException("Invalid email or password")

    token = create_access_token(user.id, user.username)

    return TokenResponse(
        success=True,
        token=token,
        user=UserPublic(name=user.username, role="System Admin"),
    )


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user account."""
    # Check if email or username already exists
    existing = db.query(User).filter(
        (User.email == request.email) | (User.username == request.username)
    ).first()

    if existing:
        raise AppException(status_code=409, message="A user with this email or username already exists")

    user = User(
        username=request.username,
        email=request.email,
        password_hash=hash_password(request.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, user.username)

    return TokenResponse(
        success=True,
        token=token,
        user=UserPublic(name=user.username, role="User"),
    )
