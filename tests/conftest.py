from typing import TYPE_CHECKING, Callable, List, Optional

import pytest
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative.api import declarative_base
from sqlalchemy.orm.session import Session, sessionmaker

if TYPE_CHECKING:
    from sqlalchemy.ext.declarative import DeclarativeMeta


@pytest.fixture
def Base() -> "DeclarativeMeta":
    return declarative_base()


@pytest.fixture
def create_db(Base) -> Callable:
    def prepare_db(instances: Optional[List["DeclarativeMeta"]] = None) -> Session:
        instances = instances or []

        engine = create_engine("sqlite://", echo=True)
        Base.metadata.create_all(engine)
        LocalSession = sessionmaker(bind=engine)

        session = LocalSession()
        session.add_all(instances)
        session.commit()

        return session

    return prepare_db
