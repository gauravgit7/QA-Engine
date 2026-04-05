import json
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional

from database.connection import get_db
from database.models import User, TestCaseHistory, Configuration, Document
from models.schemas import GenerateResponse, TestCaseItem
from services.llm_service import generate_test_cases
from services.file_service import extract_text_from_file, extract_text_with_metadata
from services.document_analyzer import analyze_document
from services.coverage_analyzer import analyze_coverage
from utils.dependencies import get_current_user
from utils.exceptions import ValidationException

router = APIRouter(prefix="/generate", tags=["Test Case Generation"])


@router.post("/uat", response_model=GenerateResponse)
async def generate_uat_cases(
    file: Optional[UploadFile] = File(None),
    manual_text: Optional[str] = Form(None),
    epic_id: Optional[str] = Form(None),
    story_id: Optional[str] = Form(None),
    test_case_id: Optional[str] = Form(None),
    generation_method: Optional[str] = Form("rules"),
    target_count: Optional[int] = Form(50),
    domain_hint: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate comprehensive UAT test cases from BRD/PRD document or manual text."""
    context_text = ""
    doc_stats = None

    # Extract text from uploaded file
    if file and file.filename:
        file_bytes = await file.read()
        if file_bytes:
            meta = extract_text_with_metadata(file_bytes, file.filename)
            context_text = meta["text"]
            doc_stats = {
                "filename": meta["filename"],
                "file_type": meta["file_type"],
                "word_count": meta["word_count"],
                "page_count": meta["page_count"],
                "section_count": meta["section_count"],
            }

    # Append manual text
    if manual_text and manual_text.strip():
        context_text = context_text + "\n\n" + manual_text.strip() if context_text else manual_text.strip()

    if not context_text.strip():
        raise ValidationException("Either a file upload or manual text input is required.")

    config = db.query(Configuration).filter(Configuration.user_id == current_user.id).first()
    api_key_from_db = config.llm_api_key if config else None
    ollama_model_from_db = config.ollama_model if config else settings.OLLAMA_MODEL

    # Build options
    options = {
        "test_case_count": min(target_count or 50, 100),
        "include_negative": True,
        "include_edge": True,
    }

    # Generate test cases
    raw_cases, metadata = await generate_test_cases(
        context_text=context_text,
        module_type="UAT",
        epic_id=epic_id,
        story_id=story_id,
        base_test_id=test_case_id or "TC-UAT",
        api_key=api_key_from_db,
        generation_method=generation_method or "rules",
        options=options,
        ollama_model=ollama_model_from_db,
    )

    # Run coverage analysis
    analysis = analyze_document(context_text)
    coverage = analyze_coverage(raw_cases, analysis)

    # Apply domain hint override if provided
    domain_detected = domain_hint or analysis.get("domain", "generic")

    # Map to schema
    test_cases = [TestCaseItem(**tc) for tc in raw_cases]

    # Save document record
    doc_record = Document(
        user_id=current_user.id,
        name=file.filename if (file and file.filename) else "Manual Input",
        file_type=doc_stats.get("file_type", "txt") if doc_stats else "txt",
        domain=domain_detected,
        word_count=doc_stats.get("word_count", len(context_text.split())) if doc_stats else len(context_text.split()),
        page_count=doc_stats.get("page_count", 0) if doc_stats else 0,
        requirement_count=len(analysis.get("requirements", [])),
        role_count=len(analysis.get("user_roles", [])),
        module_count=len(analysis.get("modules", [])),
        parsed_structure=json.dumps({"sections": analysis.get("sections", []), "modules": analysis.get("modules", [])}),
        processing_status="generated",
    )
    db.add(doc_record)
    db.flush()

    # Save to history
    history_entry = TestCaseHistory(
        user_id=current_user.id,
        module_type="UAT",
        input_data=context_text[:2000],
        generated_output=json.dumps(raw_cases),
        method_used=metadata.get("method_used"),
        confidence_score=0.9,
        token_usage=metadata.get("token_usage", 0),
        cost=metadata.get("cost", 0.0),
        fallback_triggered=metadata.get("fallback_triggered", False),
        document_id=doc_record.id,
        domain_detected=domain_detected,
        total_requirements=len(analysis.get("requirements", [])),
        coverage_percentage=coverage.get("overall_coverage_percentage", 0.0),
    )
    db.add(history_entry)
    db.commit()

    return GenerateResponse(
        success=True,
        testCases=test_cases,
        method_used=metadata.get("method_used", ""),
        fallback_triggered=metadata.get("fallback_triggered", False),
        fallback_reason=metadata.get("fallback_reason"),
        generation_time=metadata.get("generation_time", 0.0),
        token_usage=metadata.get("token_usage", 0),
        cost=metadata.get("cost", 0.0),
        total_generated=len(test_cases),
        domain_detected=domain_detected,
        total_requirements_found=len(analysis.get("requirements", [])),
        coverage_percentage=coverage.get("overall_coverage_percentage", 0.0),
        coverage_report=coverage,
        document_stats=doc_stats,
    )


@router.post("/story", response_model=GenerateResponse)
async def generate_story_cases(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    story_id: Optional[str] = Form(None),
    generation_method: Optional[str] = Form("llm"),
    options: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate test cases from a user story or feature description."""
    context_text = ""

    # Extract text from uploaded file
    if file and file.filename:
        file_bytes = await file.read()
        if file_bytes:
            context_text = extract_text_from_file(file_bytes, file.filename)

    # Append story text
    if text and text.strip():
        context_text = context_text + "\n\n" + text.strip() if context_text else text.strip()

    if not context_text.strip():
        raise ValidationException("Story context text is required.")

    config = db.query(Configuration).filter(Configuration.user_id == current_user.id).first()
    api_key_from_db = config.llm_api_key if config else None
    ollama_model_from_db = config.ollama_model if config else settings.OLLAMA_MODEL

    options_dict = json.loads(options) if options else {}

    # Generate test cases via LLM
    raw_cases, metadata = await generate_test_cases(
        context_text=context_text,
        module_type="STORY",
        story_id=story_id,
        api_key=api_key_from_db,
        generation_method=generation_method,
        options=options_dict,
        ollama_model=ollama_model_from_db
    )

    test_cases = [TestCaseItem(**tc) for tc in raw_cases]

    # Save to history
    history_entry = TestCaseHistory(
        user_id=current_user.id,
        module_type="STORY",
        input_data=context_text[:2000],
        generated_output=json.dumps(raw_cases),
        method_used=metadata.get("method_used"),
        confidence_score=0.9,
        token_usage=metadata.get("token_usage", 0),
        cost=metadata.get("cost", 0.0),
        fallback_triggered=metadata.get("fallback_triggered", False)
    )
    db.add(history_entry)
    db.commit()

    return GenerateResponse(
        success=True,
        testCases=test_cases,
        method_used=metadata.get("method_used", ""),
        fallback_triggered=metadata.get("fallback_triggered", False),
        fallback_reason=metadata.get("fallback_reason"),
        generation_time=metadata.get("generation_time", 0.0),
        token_usage=metadata.get("token_usage", 0),
        cost=metadata.get("cost", 0.0),
        total_generated=len(test_cases),
    )
