from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("", response_model=ApiResponse[list[dict]])
def recommendations(
    member_id: str | None = Query(default=None),
    limit: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    target_member_id = member_id or user.id
    service = RecommendationService(db)
    recs = service.recommend_for_member(target_member_id, limit=limit)
    return ApiResponse(data=[r.to_dict() for r in recs])
