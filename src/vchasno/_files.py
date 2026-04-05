"""Shared file-handling utilities for upload endpoints."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Any, BinaryIO, Generator


@contextmanager
def open_file(
    file: str | Path | BinaryIO,
    *,
    default_name: str = "document",
    filename: str | None = None,
) -> Generator[tuple[str, BinaryIO], None, None]:
    """Open a file path or pass through a BinaryIO, ensuring cleanup on exit.

    Yields:
        (resolved_filename, file_object) tuple ready for use in multipart uploads.
    """
    if isinstance(file, (str, Path)):
        path = Path(file)
        resolved_name = filename or path.name
        fp: BinaryIO = open(path, "rb")  # noqa: SIM115
        try:
            yield resolved_name, fp
        finally:
            fp.close()
    else:
        yield (filename or default_name), file


@contextmanager
def open_files(
    files: list[str | Path | BinaryIO],
    *,
    field_name: str = "files",
    default_name: str = "file",
) -> Generator[list[tuple[str, tuple[str, BinaryIO]]], None, None]:
    """Open multiple files, yielding a list of (field_name, (filename, fp)) tuples.

    Ensures all opened file handles are closed on exit, even if an error occurs.
    """
    opened: list[BinaryIO] = []
    file_tuples: list[tuple[str, tuple[str, BinaryIO]]] = []
    try:
        for f in files:
            if isinstance(f, (str, Path)):
                p = Path(f)
                fp = open(p, "rb")  # noqa: SIM115
                opened.append(fp)
                file_tuples.append((field_name, (p.name, fp)))
            else:
                file_tuples.append((field_name, (default_name, f)))
        yield file_tuples
    finally:
        for fp in opened:
            fp.close()
