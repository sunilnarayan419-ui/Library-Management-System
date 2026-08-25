from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.book_copy import CopyStatus


class BookCopyOut(BaseModel):
    id: str
    accession_number: str
    status: CopyStatus
    location: str | None = None
    condition: str

    model_config = {"from_attributes": True}


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    author: str = Field(min_length=1, max_length=200)
    isbn: str | None = Field(default=None, max_length=20)
    publisher: str | None = None
    publication_year: int | None = None
    category: str | None = None
    description: str | None = None
    language: str = "English"
    initial_copies: int = Field(default=1, ge=0, le=1000)


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    isbn: str | None = None
    publisher: str | None = None
    publication_year: int | None = None
    category: str | None = None
    description: str | None = None
    language: str | None = None


class BookOut(BaseModel):
    id: str
    isbn: str | None
    title: str
    author: str
    publisher: str | None
    publication_year: int | None
    category: str | None
    description: str | None
    language: str
    total_copies: int
    available_copies: int

    model_config = {"from_attributes": True}


class BookCopyCreate(BaseModel):
    accession_number: str
    location: str | None = None
    condition: str = "GOOD"
