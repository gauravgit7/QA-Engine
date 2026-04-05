from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.connection import get_db
from database.models import User, TestCaseHistory
from models.schemas import DashboardResponse, DashboardStats
from utils.dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardResponse)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get aggregate statistics for the dashboard cards and charts."""

    # Total generated test case batches
    total_generated = db.query(TestCaseHistory).filter(
        TestCaseHistory.user_id == current_user.id
    ).count()

    # Generated this week
    one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    this_week = db.query(TestCaseHistory).filter(
        TestCaseHistory.user_id == current_user.id,
        TestCaseHistory.created_at >= one_week_ago,
    ).count()

    # Jira synced count
    jira_synced = db.query(TestCaseHistory).filter(
        TestCaseHistory.user_id == current_user.id,
        TestCaseHistory.module_type == "JIRA",
    ).count()

    # Active users (total user count as a proxy)
    active_users = db.query(func.count(User.id)).scalar() or 0

    stats = DashboardStats(
        totalGenerated=total_generated,
        thisWeek=this_week,
        jiraSynced=jira_synced,
        activeUsers=active_users,
    )

    return DashboardResponse(success=True, stats=stats)
