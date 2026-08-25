"""Generic repository interface (Protocol) that concrete SQLAlchemy
repositories implement. Keeping this as a Protocol lets services depend
on an abstraction rather than SQLAlchemy directly, which keeps the
door open for swapping persistence technology later.
"""
from __future__ import annotations

from typing import Protocol, TypeVar

T = TypeVar("T")


class Repository(Protocol[T]):
    def get(self, id: str) -> T | None: ...

    def list(self, **filters: object) -> list[T]: ...

    def add(self, entity: T) -> T: ...

    def delete(self, entity: T) -> None: ...
