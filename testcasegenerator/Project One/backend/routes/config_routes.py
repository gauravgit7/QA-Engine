from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import User, Configuration
from models.schemas import ConfigSaveRequest, ConfigResponse, ConfigSaveResponse
from utils.dependencies import get_current_user

router = APIRouter(prefix="/config", tags=["Configuration"])


def _mask_value(value: str) -> str:
    """Mask sensitive values, showing only the last 4 characters."""
    if not value or len(value) <= 4:
        return "••••" if value else ""
    return "•" * (len(value) - 4) + value[-4:]


@router.post("/save", response_model=ConfigSaveResponse)
async def save_config(
    request: ConfigSaveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save or update the user's Jira and LLM configuration."""
    config = db.query(Configuration).filter(Configuration.user_id == current_user.id).first()

    if config:
        # Update existing config
        if request.jira_base_url is not None:
            config.jira_base_url = request.jira_base_url
        if request.jira_email is not None:
            config.jira_email = request.jira_email
        # Only update token/key if a new non-masked value is provided
        if request.jira_api_token and "•" not in request.jira_api_token:
            config.jira_api_token = request.jira_api_token
        if request.llm_api_key and "•" not in request.llm_api_key:
            config.llm_api_key = request.llm_api_key
        if request.ollama_model is not None:
            config.ollama_model = request.ollama_model
    else:
        # Create new config
        config = Configuration(
            user_id=current_user.id,
            jira_base_url=request.jira_base_url or "",
            jira_email=request.jira_email or "",
            jira_api_token=request.jira_api_token or "",
            llm_api_key=request.llm_api_key or "",
            ollama_model=request.ollama_model or "dolphin-llama3:latest",
        )
        db.add(config)

    db.commit()

    return ConfigSaveResponse(success=True, message="Configuration saved successfully.")


@router.get("", response_model=ConfigResponse)
async def get_config(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve the user's configuration with sensitive fields masked."""
    config = db.query(Configuration).filter(Configuration.user_id == current_user.id).first()

    if not config:
        return ConfigResponse(success=True)

    return ConfigResponse(
        success=True,
        jira_base_url=config.jira_base_url or "",
        jira_email=config.jira_email or "",
        jira_api_token=_mask_value(config.jira_api_token),
        llm_api_key=_mask_value(config.llm_api_key),
        ollama_model=config.ollama_model or "dolphin-llama3:latest",
    )


@router.get("/ollama/status")
async def get_ollama_status(current_user: User = Depends(get_current_user)):
    """Check if the local Ollama AI engine is running and responsive."""
    from services.llm_service import is_ollama_running
    is_running = await is_ollama_running()
    return {
        "success": True,
        "is_running": is_running,
        "message": "AI Engine is Ready" if is_running else "AI Engine is Offline"
    }


@router.post("/ollama/start")
async def start_ollama_engine(current_user: User = Depends(get_current_user)):
    """Initiate/Warm up the Ollama AI engine."""
    from services.llm_service import warmup_ollama, is_ollama_running
    import subprocess
    import time
    
    # 1. Check if already running
    if await is_ollama_running():
        # Just warm it up
        success = await warmup_ollama()
        return {"success": success, "message": "AI Engine warmed up and ready."}
        
    # 2. Try to start the serve process (platform dependent)
    try:
        # Start ollama serve in a detached process
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        
        # 3. Wait a few seconds for it to bind to the port
        for _ in range(5):
            time.sleep(2)
            if await is_ollama_running():
                break
        
        # 4. Warm up the model
        if await is_ollama_running():
            success = await warmup_ollama()
            return {"success": success, "message": "AI Engine started and warmed up."}
        else:
            return {"success": False, "message": "Failed to start Ollama. Ensure Ollama is installed and in your PATH."}
            
    except Exception as e:
        return {"success": False, "message": f"Error starting AI Engine: {str(e)}"}
