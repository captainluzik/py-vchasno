"""Shared file-handling utilities for upload endpoints."""

from __future__ import annotations

from collections.abc import Generator, Sequence
from contextlib import contextmanager
from pathlib import Path
from typing import IO


@contextmanager
def open_file(
    file: str | Path | IO[bytes],
    *,
    default_name: str = "document",
    filename: str | None = None,
) -> Generator[tuple[str, IO[bytes]], None, None]:
    """Open a file path or pass through a file object, ensuring cleanup on exit.

    Yields:
        (resolved_filename, file_object) tuple ready for use in multipart uploads.
    """
    if isinstance(file, (str, Path)):
        path = Path(file)
        resolved_name = filename or path.name
        fp: IO[bytes] = open(path, "rb")
        try:
            yield resolved_name, fp
        finally:
            fp.close()
    else:
        yield (filename or default_name), file


@contextmanager
def open_files(
    files: Sequence[str | Path | IO[bytes]],
    *,
    field_name: str = "files",
    default_name: str = "file",
) -> Generator[list[tuple[str, tuple[str, IO[bytes]]]], None, None]:
    """Open multiple files, yielding a list of (field_name, (filename, fp)) tuples.

    Ensures all opened file handles are closed on exit, even if an error occurs.
    """
    opened: list[IO[bytes]] = []
    file_tuples: list[tuple[str, tuple[str, IO[bytes]]]] = []
    try:
        for f in files:
            if isinstance(f, (str, Path)):
                p = Path(f)
                fp = open(p, "rb")
                opened.append(fp)
                file_tuples.append((field_name, (p.name, fp)))
            else:
                file_tuples.append((field_name, (default_name, f)))
        yield file_tuples
    finally:
        for fp in opened:
            fp.close()
