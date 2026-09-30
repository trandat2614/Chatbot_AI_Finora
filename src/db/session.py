"""Database engine/session lifecycle with SQLite local and PostgreSQL production support."""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import Session, sessionmaker

from config.settings import settings
from src.db.base import Base


class Database:
    def __init__(self, url: str | None = None) -> None:
        self.url = url or settings.DATABASE_URL
        parsed = make_url(self.url)
        connect_args: dict = {}
        if parsed.drivername.startswith("sqlite"):
            connect_args["check_same_thread"] = False
            if parsed.database and parsed.database != ":memory:":
                database_path = Path(parsed.database)
                if not database_path.is_absolute():
                    database_path = settings.BASE_DIR / database_path
                    self.url = str(parsed.set(database=str(database_path)))
                database_path.parent.mkdir(parents=True, exist_ok=True)
        self.engine: Engine = create_engine(
            self.url,
            pool_pre_ping=True,
            connect_args=connect_args,
        )
        self.session_factory = sessionmaker(
            bind=self.engine, class_=Session, expire_on_commit=False, autoflush=False
        )

    def create_schema(self) -> None:
        from src.db import models  # noqa: F401

        Base.metadata.create_all(self.engine)

    @contextmanager
    def session(self) -> Iterator[Session]:
        db = self.session_factory()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def dispose(self) -> None:
        self.engine.dispose()


_database: Database | None = None


def get_database() -> Database:
    global _database
    if _database is None:
        _database = Database()
    return _database


def reset_database(database: Database | None = None) -> None:
    global _database
    if _database is not None:
        _database.dispose()
    _database = database
