"""Temporary raw-upload retention with generated paths and guaranteed cleanup."""
from __future__ import annotations

import os
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from config.settings import settings


class RawUploadService:
    def __init__(self, root: Path | None = None, retention_hours: int | None = None) -> None:
        self.root = (root or settings.get_raw_upload_dir()).resolve()
        self.retention_hours = max(
            retention_hours
            if retention_hours is not None
            else settings.RAW_UPLOAD_RETENTION_HOURS,
            0,
        )

    def cleanup_expired(self) -> int:
        if not self.root.exists():
            return 0
        cutoff = time.time() - self.retention_hours * 3600
        removed = 0
        for path in self.root.glob("upload-*"):
            try:
                resolved = path.resolve()
                if resolved.parent != self.root or not resolved.is_file():
                    continue
                if self.retention_hours == 0 or resolved.stat().st_mtime < cutoff:
                    resolved.unlink()
                    removed += 1
            except OSError:
                continue
        return removed

    @contextmanager
    def temporary_copy(self, suffix: str, contents: bytes) -> Iterator[Path]:
        self.root.mkdir(parents=True, exist_ok=True)
        safe_suffix = suffix.lower() if suffix.lower() in {".csv", ".xlsx", ".xls"} else ".bin"
        path = (self.root / f"upload-{uuid.uuid4().hex}{safe_suffix}").resolve()
        if path.parent != self.root:
            raise ValueError("Temporary upload path escaped configured root.")
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(contents)
            yield path
        finally:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
