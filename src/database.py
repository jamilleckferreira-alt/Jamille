from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from streamlit.errors import StreamlitSecretNotFoundError

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


def _mysql_connect_args() -> dict[str, dict[str, str]]:
    ca_file = os.getenv("MYSQL_SSL_CA")
    if not ca_file:
        try:
            ca_file = st.secrets.get("MYSQL_SSL_CA")
        except StreamlitSecretNotFoundError:
            ca_file = None

    if not ca_file:
        return {}

    ca_path = Path(ca_file).expanduser()
    if not ca_path.is_absolute():
        ca_path = Path(__file__).resolve().parent.parent / ca_path
    if not ca_path.is_file():
        raise FileNotFoundError(f"Certificado CA MySQL não encontrado: {ca_path}")

    return {"ssl": {"ca": str(ca_path)}}


database_url = get_database_url()
connect_args = _mysql_connect_args() if database_url.startswith("mysql+") else {}
engine = create_engine(
    database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()
