# Pydantic-SQLAlchemy

<a href="https://github.com/Chise1/pydantic-sqlalchemy/actions?query=workflow%3ATest" target="_blank">
    <img src="https://github.com/Chise1/pydantic-sqlalchemy/workflows/Test/badge.svg" alt="Test">
</a>
<a href="https://codecov.io/gh/Chise1/pydantic-sqlalchemy" target="_blank">
    <img src="https://img.shields.io/codecov/c/github/Chise1/pydantic-sqlalchemy?color=%2334D058" alt="Coverage">
</a>
<a href="https://pypi.org/project/sqlalchemy-dantic" target="_blank">
    <img src="https://img.shields.io/pypi/v/sqlalchemy-dantic?color=%2334D058&label=pypi%20package" alt="Package version">
</a>

Tools to generate Pydantic models from SQLAlchemy models.

Still experimental.
## Install
```shell script
pip3 install sqlalchemy-dantic
```

## How to use

Quick example:

```Python
from typing import List

from sqlalchemy_dantic import sqlalchemy_to_pydantic
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker

Base = declarative_base()

engine = create_engine("sqlite://", echo=True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)

    addresses = relationship(
        "Address", back_populates="user", cascade="all, delete, delete-orphan"
    )


class Address(Base):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="addresses")


PydanticUser = sqlalchemy_to_pydantic(User,name="PydanticUser")
PydanticAddress = sqlalchemy_to_pydantic(Address,name="PydanticAddress")


class PydanticUserWithAddresses(PydanticUser):
    addresses: List[PydanticAddress] = []


Base.metadata.create_all(engine)


LocalSession = sessionmaker(bind=engine)

db: Session = LocalSession()

ed_user = User(name="ed", fullname="Ed Jones", nickname="edsnickname")

address = Address(email_address="ed@example.com")
address2 = Address(email_address="eddy@example.com")
ed_user.addresses = [address, address2]
db.add(ed_user)
db.commit()


def test_sqlalchemy_dantic():
    user = db.query(User).first()
    pydantic_user = PydanticUser.from_orm(user)
    data = pydantic_user.dict()
    assert data == {
        "fullname": "Ed Jones",
        "id": 1,
        "name": "ed",
        "nickname": "edsnickname",
    }
    pydantic_user_with_addresses = PydanticUserWithAddresses.from_orm(user)
    data = pydantic_user_with_addresses.dict()
    assert data == {
        "fullname": "Ed Jones",
        "id": 1,
        "name": "ed",
        "nickname": "edsnickname",
        "addresses": [
            {"email_address": "ed@example.com", "id": 1, "user_id": 1},
            {"email_address": "eddy@example.com", "id": 2, "user_id": 1},
        ],
    }
```

## Release Notes
### add sub Schema .
## License

This project is licensed under the terms of the MIT license.
