from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_permission
from app.database.session import get_db
from app.models.user import User
from app.schemas.analytics import CategoryShare, DashboardSummary, MonthlyCirculation, TopBook
from app.schemas.common import ApiResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=ApiResponse[DashboardSummary])
def dashboard(db: Session = Depends(get_db), _user: User = Depends(require_permission("analytics:view"))):
    service = AnalyticsService(db)
    return ApiResponse(data=service.dashboard_summary())


@router.get("/top-books", response_model=ApiResponse[list[TopBook]])
def top_books(db: Session = Depends(get_db), _user: User = Depends(require_permission("analytics:view"))):
    service = AnalyticsService(db)
    return ApiResponse(data=service.most_borrowed_books())


@router.get("/categories", response_model=ApiResponse[list[CategoryShare]])
def categories(db: Session = Depends(get_db), _user: User = Depends(require_permission("analytics:view"))):
    service = AnalyticsService(db)
    return ApiResponse(data=service.category_distribution())


@router.get("/monthly-circulation", response_model=ApiResponse[list[MonthlyCirculation]])
def monthly_circulation(db: Session = Depends(get_db), _user: User = Depends(require_permission("analytics:view"))):
    service = AnalyticsService(db)
    return ApiResponse(data=service.monthly_circulation())
