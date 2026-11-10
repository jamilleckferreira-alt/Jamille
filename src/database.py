from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

load_dotenv()


class Base(DeclarativeBase):
    pass


def _sqlite_url() -> str:
    db_path = Path(__file__).resolve().parent.parent / "festival_local.db"
    return f"sqlite:///{db_path.as_posix()}"


def _mysql_url() -> str:
    user = os.getenv("MYSQL_USER", "")
    password = os.getenv("MYSQL_PASSWORD", "")
    host = os.getenv("MYSQL_HOST", "localhost")
    port = os.getenv("MYSQL_PORT", "3306")
    database = os.getenv("MYSQL_DATABASE", "festival_ifc")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"


def get_database_url() -> str:
    production_flag = os.getenv("STREAMLIT_ENV", "").lower() == "production"
    mysql_configured = all(
        os.getenv(name)
        for name in ["MYSQL_HOST", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DATABASE"]
    )
    if production_flag or mysql_configured:
        return _mysql_url()
    return _sqlite_url()


engine = create_engine(get_database_url(), pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()
