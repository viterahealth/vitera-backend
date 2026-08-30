"""
Sync SQLAlchemy engine + session, pointed at TiDB via pymysql.

TiDB Cloud requires TLS on port 4000. pymysql takes SSL settings as
connect_args, not as URL query params, so it's configured here.
"""
import ssl as ssl_lib

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from core.config import settings

connect_args = {}
if settings.DB_SSL:
    ssl_context = ssl_lib.create_default_context()
    connect_args["ssl"] = ssl_context

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,   # avoids "server has gone away" on idle connections
    pool_recycle=280,     # TiDB Cloud serverless can close idle conns ~5min
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()