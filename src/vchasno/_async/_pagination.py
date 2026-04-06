"""Cursor-based pagination iterator."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar

from pydantic import BaseModel

if TYPE_CHECKING:
    from vchasno._async._http import AsyncTransport

T = TypeVar("T", bound=BaseModel)


class AsyncCursorPage(Generic[T]):
    """Cursor-based page with auto-iteration support.

    Fetches items lazily page-by-page using a cursor token.
    Supports both direct page access and ``async for`` / ``for``
    iteration over all items across all pages.

    Backward-compatible: accessing the attribute matching *data_key*
    (e.g. ``.documents``, ``.comments``, ``.directories``) returns
    the same list as ``.data``.
    """

    def __init__(
        self,
        data: list[T],
        next_cursor: str | None,
        *,
        transport: AsyncTransport,
        path: str,
        params: dict[str, Any],
        model_cls: type[T],
        data_key: str = "documents",
    ) -> None:
        self.data = data
        self.next_cursor = next_cursor
        self._transport = transport
        self._path = path
        self._params = params
        self._model_cls = model_cls
        self._data_key = data_key

    # -- factory --------------------------------------------------------

    @classmethod
    def _from_response(
        cls,
        raw: dict[str, Any],
        *,
        model_cls: type[T],
        transport: AsyncTransport,
        path: str,
        params: dict[str, Any],
        data_key: str = "documents",
    ) -> AsyncCursorPage[T]:
        """Build a page from a raw API JSON response."""
        items = [model_cls.model_validate(item) for item in raw.get(data_key, [])]
        return cls(
            data=items,
            next_cursor=raw.get("next_cursor"),
            transport=transport,
            path=path,
            params=params,
            model_cls=model_cls,
            data_key=data_key,
        )

    # -- backward-compat alias ------------------------------------------

    def __getattr__(self, name: str) -> Any:
        """Return ``data`` when accessed via the original collection key."""
        data_key = object.__getattribute__(self, "_data_key")
        if name == data_key:
            return object.__getattribute__(self, "data")
        raise AttributeError(f"'{type(self).__name__}' object has no attribute {name!r}")

    # -- pagination -----------------------------------------------------

    def has_next_page(self) -> bool:
        """Return ``True`` if a next page is available."""
        return self.next_cursor is not None

    async def get_next_page(self) -> AsyncCursorPage[T]:
        """Fetch the next page using the cursor token.

        Raises:
            StopAsyncIteration: When no next page is available.
        """
        if self.next_cursor is None:
            raise StopAsyncIteration
        params = {**self._params, "cursor": self.next_cursor}
        resp = await self._transport.request("GET", self._path, params=params)
        raw: dict[str, Any] = resp.json()
        return AsyncCursorPage._from_response(
            raw,
            model_cls=self._model_cls,
            transport=self._transport,
            path=self._path,
            params=self._params,
            data_key=self._data_key,
        )

    def __aiter__(self) -> AsyncCursorPage[T]:
        self._current_page: AsyncCursorPage[T] = self
        self._index = 0
        return self

    async def __anext__(self) -> T:
        while True:
            if self._index < len(self._current_page.data):
                item = self._current_page.data[self._index]
                self._index += 1
                return item
            if not self._current_page.has_next_page():
                raise StopAsyncIteration
            self._current_page = await self._current_page.get_next_page()
            self._index = 0
