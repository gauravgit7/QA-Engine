import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import User, TestCaseHistory, Configuration
from models.schemas import GenerateResponse, TestCaseItem, JiraGenerateResponse
from services.jira_service import fetch_jira_story
from services.llm_service import generate_test_cases
from utils.dependencies import get_current_user
from utils.exceptions import ValidationException, ExternalServiceException

router = APIRouter(prefix="/jira", tags=["Jira Integration"])


@router.get("/story/{story_id}", response_model=JiraGenerateResponse)
async def generate_from_jira(
    story_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch a Jira story by ID and generate test cases from its content."""
    if not story_id or not story_id.strip():
        raise ValidationException("Jira Story ID is required.")

    # Get stored Jira configuration
    config = db.query(Configuration).filter(Configuration.user_id == current_user.id).first()

    jira_base_url = config.jira_base_url if config else ""
    jira_email = config.jira_email if config else ""
    jira_token = config.jira_api_token if config else ""

    # Fetch story from Jira (or mock)
    try:
        story_data = fetch_jira_story(jira_base_url, jira_email, jira_token, story_id)
    except Exception as e:
        raise ExternalServiceException(str(e))

    # Build context from Jira story data
    context_text = (
        f"Jira Story: {story_data['key']}\n"
        f"Title: {story_data['title']}\n"
        f"Status: {story_data['status']}\n"
        f"Priority: {story_data['priority']}\n\n"
        f"Description:\n{story_data['description']}\n\n"
        f"Acceptance Criteria:\n{story_data.get('acceptance_criteria', 'N/A')}"
    )

    llm_api_key = config.llm_api_key if config else None
    ollama_model = config.ollama_model if config else settings.OLLAMA_MODEL

    # Generate test cases via LLM
    raw_cases = await generate_test_cases(
        context_text=context_text,
        module_type="JIRA",
        story_id=story_id,
        api_key=llm_api_key,
        ollama_model=ollama_model
    )

    test_cases = [TestCaseItem(**tc) for tc in raw_cases]

    # Save to history
    history_entry = TestCaseHistory(
        user_id=current_user.id,
        module_type="JIRA",
        input_data=json.dumps({"jira_story_id": story_id, "title": story_data["title"]}),
        generated_output=json.dumps(raw_cases),
    )
    db.add(history_entry)
    db.commit()

    return JiraGenerateResponse(
        success=True,
        testCases=test_cases,
        storyTitle=story_data["title"],
    )
