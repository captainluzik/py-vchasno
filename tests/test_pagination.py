"""Tests for cursor-based pagination — async and sync variants."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from helpers import make_response
from pydantic import BaseModel

from vchasno._async._pagination import AsyncCursorPage
from vchasno._sync._pagination import SyncCursorPage


class Item(BaseModel):
    id: int
    name: str


def _page_response(items: list[dict[str, Any]], next_cursor: str | None = None) -> dict[str, Any]:
    return {"documents": items, "next_cursor": next_cursor}


# ---------------------------------------------------------------------------
# AsyncCursorPage
# ---------------------------------------------------------------------------


class TestAsyncCursorPage:
    @pytest.fixture()
    def transport(self) -> MagicMock:
        t = MagicMock()
        t.request = AsyncMock()
        return t

    def _make_page(
        self,
        transport: MagicMock,
        items: list[Item],
        next_cursor: str | None = None,
    ) -> AsyncCursorPage[Item]:
        return AsyncCursorPage(
            data=items,
            next_cursor=next_cursor,
            transport=transport,
            path="/items",
            params={},
            model_cls=Item,
        )

    @pytest.mark.asyncio()
    async def test_single_page_iteration(self, transport: MagicMock) -> None:
        page = self._make_page(transport, [Item(id=1, name="a"), Item(id=2, name="b")])

        collected: list[Item] = []
        async for item in page:
            collected.append(item)

        assert len(collected) == 2
        assert collected[0].id == 1
        assert collected[1].id == 2
        transport.request.assert_not_called()

    @pytest.mark.asyncio()
    async def test_two_page_iteration(self, transport: MagicMock) -> None:
        page2_data = _page_response([{"id": 3, "name": "c"}])
        transport.request.return_value = make_response(json_data=page2_data)

        page = self._make_page(
            transport,
            [Item(id=1, name="a"), Item(id=2, name="b")],
            next_cursor="cursor-2",
        )

        collected: list[Item] = []
        async for item in page:
            collected.append(item)

        assert len(collected) == 3
        assert [i.id for i in collected] == [1, 2, 3]
        transport.request.assert_called_once_with("GET", "/items", params={"cursor": "cursor-2"})

    @pytest.mark.asyncio()
    async def test_has_next_page(self, transport: MagicMock) -> None:
        page_with = self._make_page(transport, [], next_cursor="x")
        page_without = self._make_page(transport, [])

        assert page_with.has_next_page() is True
        assert page_without.has_next_page() is False

    @pytest.mark.asyncio()
    async def test_get_next_page_raises_on_none_cursor(self, transport: MagicMock) -> None:
        page = self._make_page(transport, [])

        with pytest.raises(StopAsyncIteration):
            await page.get_next_page()

    @pytest.mark.asyncio()
    async def test_empty_page_no_iteration(self, transport: MagicMock) -> None:
        page = self._make_page(transport, [])

        collected: list[Item] = []
        async for item in page:
            collected.append(item)

        assert collected == []

    def test_from_response(self, transport: MagicMock) -> None:
        raw = {"documents": [{"id": 1, "name": "a"}], "next_cursor": "cur2"}
        page = AsyncCursorPage._from_response(
            raw,
            model_cls=Item,
            transport=transport,
            path="/items",
            params={"limit": 10},
        )
        assert len(page.data) == 1
        assert page.data[0].id == 1
        assert page.next_cursor == "cur2"
        assert page.has_next_page() is True

    def test_from_response_custom_data_key(self, transport: MagicMock) -> None:
        raw = {"directories": [{"id": 1, "name": "d"}], "next_cursor": None}
        page = AsyncCursorPage._from_response(
            raw,
            model_cls=Item,
            transport=transport,
            path="/dirs",
            params={},
            data_key="directories",
        )
        assert len(page.data) == 1
        assert page.has_next_page() is False

    def test_backward_compat_alias(self, transport: MagicMock) -> None:
        page = self._make_page(transport, [Item(id=1, name="a")])
        assert page.documents == page.data

    def test_backward_compat_alias_custom_key(self, transport: MagicMock) -> None:
        page = AsyncCursorPage(
            data=[Item(id=1, name="a")],
            next_cursor=None,
            transport=transport,
            path="/dirs",
            params={},
            model_cls=Item,
            data_key="directories",
        )
        assert page.directories == page.data
        with pytest.raises(AttributeError):
            _ = page.documents

    def test_getattr_unknown_raises(self, transport: MagicMock) -> None:
        page = self._make_page(transport, [])
        with pytest.raises(AttributeError, match="no_such_attr"):
            _ = page.no_such_attr


# ---------------------------------------------------------------------------
# SyncCursorPage
# ---------------------------------------------------------------------------


class TestSyncCursorPage:
    @pytest.fixture()
    def transport(self) -> MagicMock:
        return MagicMock()

    def _make_page(
        self,
        transport: MagicMock,
        items: list[Item],
        next_cursor: str | None = None,
    ) -> SyncCursorPage[Item]:
        return SyncCursorPage(
            data=items,
            next_cursor=next_cursor,
            transport=transport,
            path="/items",
            params={},
            model_cls=Item,
        )

    def test_single_page_iteration(self, transport: MagicMock) -> None:
        page = self._make_page(transport, [Item(id=1, name="a"), Item(id=2, name="b")])

        collected = list(page)

        assert len(collected) == 2
        assert collected[0].id == 1
        assert collected[1].id == 2
        transport.request.assert_not_called()

    def test_two_page_iteration(self, transport: MagicMock) -> None:
        page2_data = _page_response([{"id": 3, "name": "c"}])
        transport.request.return_value = make_response(json_data=page2_data)

        page = self._make_page(
            transport,
            [Item(id=1, name="a"), Item(id=2, name="b")],
            next_cursor="cursor-2",
        )

        collected = list(page)

        assert len(collected) == 3
        assert [i.id for i in collected] == [1, 2, 3]
        transport.request.assert_called_once_with("GET", "/items", params={"cursor": "cursor-2"})

    def test_has_next_page(self, transport: MagicMock) -> None:
        page_with = self._make_page(transport, [], next_cursor="x")
        page_without = self._make_page(transport, [])

        assert page_with.has_next_page() is True
        assert page_without.has_next_page() is False

    def test_get_next_page_raises_on_none_cursor(self, transport: MagicMock) -> None:
        page = self._make_page(transport, [])

        with pytest.raises(StopIteration):
            page.get_next_page()

    def test_empty_page_no_iteration(self, transport: MagicMock) -> None:
        page = self._make_page(transport, [])

        collected = list(page)

        assert collected == []
