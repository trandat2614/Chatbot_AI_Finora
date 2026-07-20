"""
Logging configuration for FINORA AI Business Advisor.

Call ``setup_logging()`` once at application startup.
All modules obtain a logger via ``logging.getLogger(__name__)``.
"""
import logging
import sys
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
) -> None:
    """Configure root logger for the application.

    Args:
        level: Logging level (default: INFO).
        log_file: Optional path to a log file. If None, logs to stderr only.
    """
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stderr)]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(
        level=level,
        format=fmt,
        datefmt=datefmt,
        handlers=handlers,
        force=True,
    )

    # Silence noisy third-party loggers
    for noisy in ("httpx", "httpcore", "chromadb", "openai", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
