from datetime import datetime, timezone

from sqlalchemy.orm import declarative_base

Base = declarative_base()


def utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)
