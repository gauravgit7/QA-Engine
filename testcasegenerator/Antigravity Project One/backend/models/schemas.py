from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field


# ──────────────────────────────────────────────
# Auth Schemas
# ──────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str = Field(..., min_length=1, description="Email or username")
    password: str = Field(..., min_length=1)


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    success: bool = True
    token: str
    user: "UserPublic"


class UserPublic(BaseModel):
    name: str
    role: str = "User"

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# Test Case Schemas
# ──────────────────────────────────────────────
class TestCaseItem(BaseModel):
    id: str
    title: str
    preconditions: str
    steps: str
    expectedResult: str
    priority: str  # High, Medium, Low
    test_type: str = "Functional"
    test_data: str = "N/A"
    postconditions: str = "N/A"
    tags: List[str] = []
    estimated_duration: int = 300  # seconds
    business_context: str = ""
    user_role: str = ""
    requirement_id: str = ""


class GenerateUATRequest(BaseModel):
    manual_text: Optional[str] = None
    epic_id: Optional[str] = None
    story_id: Optional[str] = None
    test_case_id: Optional[str] = None


class GenerateStoryRequest(BaseModel):
    text: str = Field(..., min_length=1)
    story_id: Optional[str] = None
    generation_method: str = "llm"  # llm or rules
    options: Optional[dict] = None


class GenerateResponse(BaseModel):
    success: bool = True
    testCases: List[TestCaseItem] = []
    method_used: str = ""
    fallback_triggered: bool = False
    fallback_reason: Optional[str] = None
    generation_time: float = 0.0
    token_usage: int = 0
    cost: float = 0.0
    # Enhanced metadata
    total_generated: int = 0
    domain_detected: str = ""
    total_requirements_found: int = 0
    coverage_percentage: float = 0.0
    coverage_report: Optional[Dict[str, Any]] = None
    document_stats: Optional[Dict[str, Any]] = None


# ──────────────────────────────────────────────
# Jira Schemas
# ──────────────────────────────────────────────
class JiraGenerateResponse(BaseModel):
    success: bool = True
    testCases: List[TestCaseItem] = []
    storyTitle: Optional[str] = None


# ──────────────────────────────────────────────
# Configuration Schemas
# ──────────────────────────────────────────────
class ConfigSaveRequest(BaseModel):
    jira_base_url: Optional[str] = ""
    jira_email: Optional[str] = ""
    jira_api_token: Optional[str] = ""
    llm_api_key: Optional[str] = ""
    ollama_model: Optional[str] = "dolphin-llama3:latest"


class ConfigResponse(BaseModel):
    success: bool = True
    jira_base_url: str = ""
    jira_email: str = ""
    jira_api_token: str = ""  # Masked in the route
    llm_api_key: str = ""     # Masked in the route
    ollama_model: str = "dolphin-llama3:latest"


class ConfigSaveResponse(BaseModel):
    success: bool = True
    message: str = "Configuration saved successfully."


# ──────────────────────────────────────────────
# History Schemas
# ──────────────────────────────────────────────
class HistoryItem(BaseModel):
    id: str
    date: str
    type: str
    itemsGenerated: int
    author: str

    class Config:
        from_attributes = True


class HistoryDetailItem(BaseModel):
    id: int
    date: str
    type: str
    input_data: Optional[str] = None
    testCases: List[TestCaseItem] = []
    author: str


class HistoryListResponse(BaseModel):
    success: bool = True
    history: List[HistoryItem] = []


class HistoryDetailResponse(BaseModel):
    success: bool = True
    record: Optional[HistoryDetailItem] = None


# ──────────────────────────────────────────────
# Dashboard Schemas
# ──────────────────────────────────────────────
class DashboardStats(BaseModel):
    totalGenerated: int = 0
    thisWeek: int = 0
    jiraSynced: int = 0
    activeUsers: int = 0


class DashboardResponse(BaseModel):
    success: bool = True
    stats: DashboardStats


# ──────────────────────────────────────────────
# Generic Message
# ──────────────────────────────────────────────
class MessageResponse(BaseModel):
    success: bool = True
    message: str = ""
