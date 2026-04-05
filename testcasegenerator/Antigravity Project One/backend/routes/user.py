from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.connection import get_db
from database.models import User, Configuration
from models.schemas import MessageResponse
from utils.dependencies import get_current_user

router = APIRouter(prefix="/user", tags=["User Preferences"])

class ThemeRequest(BaseModel):
    theme: str

@router.post("/theme", response_model=MessageResponse)
async def update_theme(
    request: ThemeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user theme preference."""
    config = db.query(Configuration).filter(Configuration.user_id == current_user.id).first()
    
    if config:
        config.theme = request.theme
    else:
        config = Configuration(
            user_id=current_user.id,
            theme=request.theme
        )
        db.add(config)
        
    db.commit()
    return MessageResponse(success=True, message=f"Theme set to {request.theme}.")
