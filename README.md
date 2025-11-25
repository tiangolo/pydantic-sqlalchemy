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

* 👷 Upgrade actions/checkout from v5 to v6. PR [#225](https://github.com/tiangolo/pydantic-sqlalchemy/pull/225) by [@tiangolo](https://github.com/tiangolo).
* 👷 Upgrade `latest-changes` GitHub Action and pin `actions/checkout@v5`. PR [#224](https://github.com/tiangolo/pydantic-sqlalchemy/pull/224) by [@tiangolo](https://github.com/tiangolo).
* ⬆ Bump actions/labeler from 5 to 6. PR [#208](https://github.com/tiangolo/pydantic-sqlalchemy/pull/208) by [@dependabot[bot]](https://github.com/apps/dependabot).
* ⬆ Bump actions/download-artifact from 4 to 6. PR [#219](https://github.com/tiangolo/pydantic-sqlalchemy/pull/219) by [@dependabot[bot]](https://github.com/apps/dependabot).
* ⬆ Bump pypa/gh-action-pypi-publish from 1.12.4 to 1.13.0. PR [#207](https://github.com/tiangolo/pydantic-sqlalchemy/pull/207) by [@dependabot[bot]](https://github.com/apps/dependabot).
* ⬆ Bump actions/checkout from 4 to 5. PR [#202](https://github.com/tiangolo/pydantic-sqlalchemy/pull/202) by [@dependabot[bot]](https://github.com/apps/dependabot).
* ⬆ Bump tiangolo/latest-changes from 0.3.2 to 0.4.0. PR [#198](https://github.com/tiangolo/pydantic-sqlalchemy/pull/198) by [@dependabot[bot]](https://github.com/apps/dependabot).
* ⬆ Bump typing-extensions from 4.6.1 to 4.13.2. PR [#173](https://github.com/tiangolo/pydantic-sqlalchemy/pull/173) by [@dependabot[bot]](https://github.com/apps/dependabot).
* ⬆ Bump astral-sh/setup-uv from 5 to 6. PR [#176](https://github.com/tiangolo/pydantic-sqlalchemy/pull/176) by [@dependabot[bot]](https://github.com/apps/dependabot).
* ⬆ Bump ruff from 0.9.8 to 0.11.13. PR [#182](https://github.com/tiangolo/pydantic-sqlalchemy/pull/182) by [@dependabot[bot]](https://github.com/apps/dependabot).
* Enable CI for Python 3.9 - 3.13. [af66239](https://github.com/tiangolo/pydantic-sqlalchemy/commit/af66239b3c0a949b5f1fe6a99b4f96a78e9e659c) by [@tiangolo](https://github.com/tiangolo).
* ⬆ Bump ruff from 0.7.1 to 0.9.8. PR [#156](https://github.com/tiangolo/pydantic-sqlalchemy/pull/156) by [@dependabot[bot]](https://github.com/apps/dependabot).
* ⬆ Bump astral-sh/setup-uv from 3 to 5. PR [#144](https://github.com/tiangolo/pydantic-sqlalchemy/pull/144) by [@dependabot[bot]](https://github.com/apps/dependabot).
* ⬆ Bump pypa/gh-action-pypi-publish from 1.11.0 to 1.12.4. PR [#151](https://github.com/tiangolo/pydantic-sqlalchemy/pull/151) by [@dependabot[bot]](https://github.com/apps/dependabot).
* 🔥 Drop support for Python 3.7. PR [#154](https://github.com/tiangolo/pydantic-sqlalchemy/pull/154) by [@tiangolo](https://github.com/tiangolo).
* ⬆ Bump tiangolo/latest-changes from 0.3.1 to 0.3.2. PR [#133](https://github.com/tiangolo/pydantic-sqlalchemy/pull/133) by [@dependabot[bot]](https://github.com/apps/dependabot).
* ⬆ Bump pypa/gh-action-pypi-publish from 1.10.3 to 1.11.0. PR [#127](https://github.com/tiangolo/pydantic-sqlalchemy/pull/127) by [@dependabot[bot]](https://github.com/apps/dependabot).
* ⬆ Bump ruff from 0.6.9 to 0.7.1. PR [#126](https://github.com/tiangolo/pydantic-sqlalchemy/pull/126) by [@dependabot[bot]](https://github.com/apps/dependabot).
* ⬆ Update pytest requirement from <8.0.0,>=7.0.1 to >=7.0.1,<9.0.0. PR [#104](https://github.com/tiangolo/pydantic-sqlalchemy/pull/104) by [@dependabot[bot]](https://github.com/apps/dependabot).
* 👷 Add labeler GitHub Action. PR [#102](https://github.com/tiangolo/pydantic-sqlalchemy/pull/102) by [@tiangolo](https://github.com/tiangolo).
* 🔧 Re-create Python project config, dependencies, and CI, just to make CI run. PR [#101](https://github.com/tiangolo/pydantic-sqlalchemy/pull/101) by [@tiangolo](https://github.com/tiangolo).
* ⬆ Bump actions/checkout from 2 to 4. PR [#62](https://github.com/tiangolo/pydantic-sqlalchemy/pull/62) by [@dependabot[bot]](https://github.com/apps/dependabot).
* 👷 Update issue-manager.yml GitHub Action permissions. PR [#78](https://github.com/tiangolo/pydantic-sqlalchemy/pull/78) by [@tiangolo](https://github.com/tiangolo).
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
