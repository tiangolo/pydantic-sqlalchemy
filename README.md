# Pydantic-SQLAlchemy

<a href="https://github.com/tiangolo/pydantic-sqlalchemy/actions?query=workflow%3ATest" target="_blank">
    <img src="https://github.com/tiangolo/pydantic-sqlalchemy/workflows/Test/badge.svg" alt="Test">
</a>
<a href="https://github.com/tiangolo/pydantic-sqlalchemy/actions?query=workflow%3APublish" target="_blank">
    <img src="https://github.com/tiangolo/pydantic-sqlalchemy/workflows/Publish/badge.svg" alt="Publish">
</a>
<a href="https://codecov.io/gh/tiangolo/pydantic-sqlalchemy" target="_blank">
    <img src="https://img.shields.io/codecov/c/github/tiangolo/pydantic-sqlalchemy?color=%2334D058" alt="Coverage">
</a>
<a href="https://pypi.org/project/pydantic-sqlalchemy" target="_blank">
    <img src="https://img.shields.io/pypi/v/pydantic-sqlalchemy?color=%2334D058&label=pypi%20package" alt="Package version">
</a>

Tools to generate Pydantic models from SQLAlchemy models.

Still experimental.

## 🚨 WARNING: Use SQLModel instead 🚨

[SQLModel](https://sqlmodel.tiangolo.com/) is a library that solves the same problem as this one, but in a much better way, also solving several other problems at the same time.

This project was to solve some simple use cases, to generate dynamic Pydantic models from SQLAlchemy models. But the result cannot be used very well in code as it doesn't have all the autocompletion and inline errors that a Pydantic model would have.

This was a very simple implementation, SQLModel is a much better solution, much better design and work behind it.

For most of the cases where you would use `pydantic-sqlalchemy`, you should use [SQLModel](https://sqlmodel.tiangolo.com/) instead.

## How to use

Quick example:

```Python
from typing import List

from pydantic_sqlalchemy import sqlalchemy_to_pydantic
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


PydanticUser = sqlalchemy_to_pydantic(User)
PydanticAddress = sqlalchemy_to_pydantic(Address)


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


def test_pydantic_sqlalchemy():
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

### Latest Changes

#### Docs

* 📝 Add SQLModel docs. PR [#70](https://github.com/tiangolo/pydantic-sqlalchemy/pull/70) by [@tiangolo](https://github.com/tiangolo).

#### Internal

* 👷 Update `latest-changes` GitHub Action. PR [#79](https://github.com/tiangolo/pydantic-sqlalchemy/pull/79) by [@tiangolo](https://github.com/tiangolo).
* 🔧 Add GitHub templates for discussions and issues, and security policy. PR [#76](https://github.com/tiangolo/pydantic-sqlalchemy/pull/76) by [@alejsdev](https://github.com/alejsdev).
* 👷 Add dependabot. PR [#60](https://github.com/tiangolo/pydantic-sqlalchemy/pull/60) by [@tiangolo](https://github.com/tiangolo).
* 👷 Update latest-changes GitHub Action. PR [#59](https://github.com/tiangolo/pydantic-sqlalchemy/pull/59) by [@tiangolo](https://github.com/tiangolo).

### 0.0.9

* ✨ Add `poetry-version-plugin`, remove `importlib-metadata` dependency. PR [#32](https://github.com/tiangolo/pydantic-sqlalchemy/pull/32) by [@tiangolo](https://github.com/tiangolo).

### 0.0.8.post1

* 💚 Fix setting up Poetry for GitHub Action Publish. PR [#23](https://github.com/tiangolo/pydantic-sqlalchemy/pull/23) by [@tiangolo](https://github.com/tiangolo).

### 0.0.8

* ⬆️ Upgrade `importlib-metadata` to 3.0.0. PR [#22](https://github.com/tiangolo/pydantic-sqlalchemy/pull/22) by [@tiangolo](https://github.com/tiangolo).
* 👷 Add GitHub Action latest-changes. PR [#20](https://github.com/tiangolo/pydantic-sqlalchemy/pull/20) by [@tiangolo](https://github.com/tiangolo).
* 💚 Fix GitHub Actions Poetry setup. PR [#21](https://github.com/tiangolo/pydantic-sqlalchemy/pull/21) by [@tiangolo](https://github.com/tiangolo).

### 0.0.7

* Update requirements of `importlib-metadata` to support the latest version `2.0.0`. PR [#11](https://github.com/tiangolo/pydantic-sqlalchemy/pull/11).

### 0.0.6

* Add support for SQLAlchemy extended types like [sqlalchemy-utc: UtcDateTime](https://github.com/spoqa/sqlalchemy-utc). PR [#9](https://github.com/tiangolo/pydantic-sqlalchemy/pull/9).

### 0.0.5

* Exclude columns before checking their Python types. PR [#5](https://github.com/tiangolo/pydantic-sqlalchemy/pull/5) by [@ZachMyers3](https://github.com/ZachMyers3).

### 0.0.4

* Do not include SQLAlchemy defaults in Pydantic models. PR [#4](https://github.com/tiangolo/pydantic-sqlalchemy/pull/4).

### 0.0.3

* Add support for `exclude` to exclude columns from Pydantic model. PR [#3](https://github.com/tiangolo/pydantic-sqlalchemy/pull/3).
* Add support for overriding the Pydantic `config`. PR [#1](https://github.com/tiangolo/pydantic-sqlalchemy/pull/1) by [@pyropy](https://github.com/pyropy).
* Add CI with GitHub Actions. PR [#2](https://github.com/tiangolo/pydantic-sqlalchemy/pull/2).

## License

This project is licensed under the terms of the MIT license.
