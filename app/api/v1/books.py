from __future__ import annotations

import math

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import require_permission
from app.database.session import get_db
from app.models.user import User
from app.schemas.books import BookCopyCreate, BookCopyOut, BookCreate, BookOut, BookUpdate
from app.schemas.common import ApiResponse, Page, PageMeta
from app.services.book_service import BookService

router = APIRouter(prefix="/books", tags=["books"])


@router.get("", response_model=ApiResponse[Page[BookOut]])
def list_books(
    search: str | None = Query(default=None),
    category: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _user: User = Depends(require_permission("books:view")),
):
    service = BookService(db)
    items, total = service.search_books(search, category, page, page_size)
    total_pages = max(1, math.ceil(total / page_size))
    return ApiResponse(
        data=Page(
            items=[BookOut.model_validate(b) for b in items],
            meta=PageMeta(page=page, page_size=page_size, total=total, total_pages=total_pages),
        )
    )


@router.get("/{book_id}", response_model=ApiResponse[BookOut])
def get_book(book_id: str, db: Session = Depends(get_db), _user: User = Depends(require_permission("books:view"))):
    service = BookService(db)
    book = service.get_book(book_id)
    return ApiResponse(data=BookOut.model_validate(book))


@router.post("", response_model=ApiResponse[BookOut], status_code=201)
def create_book(
    payload: BookCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("books:create")),
):
    service = BookService(db)
    book = service.create_book(actor=user, **payload.model_dump())
    db.commit()
    return ApiResponse(data=BookOut.model_validate(book), message="Book created")


@router.patch("/{book_id}", response_model=ApiResponse[BookOut])
def update_book(
    book_id: str,
    payload: BookUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("books:update")),
):
    service = BookService(db)
    book = service.update_book(book_id, actor=user, **payload.model_dump(exclude_unset=True))
    db.commit()
    return ApiResponse(data=BookOut.model_validate(book), message="Book updated")


@router.delete("/{book_id}", response_model=ApiResponse[None])
def delete_book(
    book_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("books:delete")),
):
    service = BookService(db)
    service.delete_book(book_id, actor=user)
    db.commit()
    return ApiResponse(data=None, message="Book deleted")


@router.post("/{book_id}/copies", response_model=ApiResponse[BookCopyOut], status_code=201)
def add_copy(
    book_id: str,
    payload: BookCopyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("books:update")),
):
    service = BookService(db)
    copy = service.add_copy(book_id, actor=user, **payload.model_dump())
    db.commit()
    return ApiResponse(data=BookCopyOut.model_validate(copy), message="Copy added")
