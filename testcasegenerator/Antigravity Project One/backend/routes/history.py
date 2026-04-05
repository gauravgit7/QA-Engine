import json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from database.connection import get_db
from database.models import User, TestCaseHistory
from models.schemas import (
    HistoryListResponse, HistoryItem,
    HistoryDetailResponse, HistoryDetailItem, TestCaseItem,
)
from utils.dependencies import get_current_user
from utils.exceptions import NotFoundException

router = APIRouter(prefix="/history", tags=["History"])


@router.get("", response_model=HistoryListResponse)
async def get_history(
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    module_type: Optional[str] = Query(None, description="Filter by module: UAT, STORY, JIRA"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all test case generation history for the current user, with optional filters."""
    query = db.query(TestCaseHistory).filter(TestCaseHistory.user_id == current_user.id)

    # Filter by module type
    if module_type:
        query = query.filter(TestCaseHistory.module_type == module_type.upper())

    # Filter by date using datetime range
    if date:
        try:
            filter_date = datetime.strptime(date, "%Y-%m-%d")
            next_day = filter_date + timedelta(days=1)
            query = query.filter(
                TestCaseHistory.created_at >= filter_date,
                TestCaseHistory.created_at < next_day,
            )
        except ValueError:
            pass  # Invalid date format, skip filter

    records = query.order_by(TestCaseHistory.created_at.desc()).all()

    history_items = []
    for record in records:
        # Count generated items
        try:
            output = json.loads(record.generated_output)
            items_count = len(output) if isinstance(output, list) else 0
        except (json.JSONDecodeError, TypeError):
            items_count = 0

        history_items.append(HistoryItem(
            id=f"HST-{record.id}",
            date=record.created_at.strftime("%Y-%m-%d") if record.created_at else "",
            type=record.module_type,
            itemsGenerated=items_count,
            author=current_user.username,
        ))

    return HistoryListResponse(success=True, history=history_items)


@router.get("/{record_id}", response_model=HistoryDetailResponse)
async def get_history_detail(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get detailed view of a specific history record including all generated test cases."""
    record = db.query(TestCaseHistory).filter(
        TestCaseHistory.id == record_id,
        TestCaseHistory.user_id == current_user.id,
    ).first()

    if not record:
        raise NotFoundException(f"History record with ID {record_id} not found.")

    # Parse stored test cases
    try:
        raw_cases = json.loads(record.generated_output)
        test_cases = [TestCaseItem(**tc) for tc in raw_cases] if isinstance(raw_cases, list) else []
    except (json.JSONDecodeError, TypeError):
        test_cases = []

    detail = HistoryDetailItem(
        id=record.id,
        date=record.created_at.strftime("%Y-%m-%d") if record.created_at else "",
        type=record.module_type,
        input_data=record.input_data,
        testCases=test_cases,
        author=current_user.username,
    )

    return HistoryDetailResponse(success=True, record=detail)
