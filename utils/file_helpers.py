"""
File helper utilities for FINORA AI Business Advisor.

Cross-platform utilities for working with files and directories.
"""
import os
from pathlib import Path
from typing import Optional


def ensure_dir(path: Path | str) -> Path:
    """Create a directory (and any missing parents) if it does not exist.

    Args:
        path: Directory path.

    Returns:
        The resolved ``Path`` object.
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def list_files(directory: Path | str, extensions: Optional[list[str]] = None) -> list[Path]:
    """List files in a directory, optionally filtered by extension.

    Args:
        directory: Directory to search.
        extensions: List of extensions to include, e.g. ``[".md", ".pdf"]``.
                    If None, return all files.

    Returns:
        Sorted list of matching ``Path`` objects.
    """
    d = Path(directory)
    if not d.is_dir():
        return []

    files = []
    for entry in d.iterdir():
        if entry.is_file():
            if extensions is None or entry.suffix.lower() in extensions:
                files.append(entry)

    return sorted(files)


def get_file_size_kb(path: Path | str) -> float:
    """Return the file size in kilobytes.

    Args:
        path: File path.

    Returns:
        Size in KB (0.0 if the file does not exist).
    """
    p = Path(path)
    if not p.exists():
        return 0.0
    return p.stat().st_size / 1024


def safe_read_text(path: Path | str, encoding: str = "utf-8") -> Optional[str]:
    """Read a text file, returning None on any error.

    Args:
        path: File path.
        encoding: Text encoding (default utf-8).

    Returns:
        File contents or None.
    """
    try:
        return Path(path).read_text(encoding=encoding)
    except (OSError, UnicodeDecodeError):
        return None


def resolve_path(*parts: str) -> Path:
    """Resolve a path relative to the project root.

    The project root is the parent of the ``utils`` package directory.

    Args:
        *parts: Path segments to join.

    Returns:
        Absolute ``Path``.
    """
    root = Path(__file__).parent.parent
    return root.joinpath(*parts)
