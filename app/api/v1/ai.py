from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai.librarian import AILibrarian
from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/ai", tags=["ai"])


class ChatRequest(BaseModel):
    message: str


class ChatResponseData(BaseModel):
    response: str


@router.post("/chat", response_model=ApiResponse[ChatResponseData])
def chat(payload: ChatRequest, db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    librarian = AILibrarian(db)
    reply = librarian.chat(payload.message)
    return ApiResponse(data=ChatResponseData(response=reply))
