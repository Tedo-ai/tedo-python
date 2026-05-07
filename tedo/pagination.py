"""Cursor pagination helpers."""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class CursorPage(Generic[T]):
    """A single cursor page returned by list endpoints."""

    items: list[T]
    next_cursor: str | None
    has_more: bool


def page_from_response(response: Mapping[str, Any]) -> CursorPage[dict[str, Any]]:
    raw_items = response.get("items", [])
    items = [dict(item) for item in raw_items if isinstance(item, dict)]
    raw_cursor = response.get("next_cursor")
    next_cursor = raw_cursor if isinstance(raw_cursor, str) else None
    raw_has_more = response.get("has_more")
    has_more = bool(raw_has_more) if raw_has_more is not None else next_cursor is not None
    return CursorPage(items=items, next_cursor=next_cursor, has_more=has_more)


def iter_pages(first_page: CursorPage[T], next_page: Callable[[str], CursorPage[T]]) -> Iterator[T]:
    page: CursorPage[T] | None = first_page
    while page is not None:
        yield from page.items
        if not page.has_more or not page.next_cursor:
            page = None
        else:
            page = next_page(page.next_cursor)
