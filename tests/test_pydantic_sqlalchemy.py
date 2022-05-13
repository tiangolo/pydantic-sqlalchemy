from datetime import datetime
from typing import List

from pydantic_sqlalchemy import extract_from_sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from tests.fixtures.Address import Address
from tests.fixtures.Base import Base
from tests.fixtures.User import User

engine = create_engine("sqlite://", echo=True)

Base.metadata.create_all(engine)


LocalSession = sessionmaker(bind=engine)

db: Session = LocalSession()

ed_user = User(name="ed", fullname="Ed Jones", nickname="edsnickname")

address = Address(email_address="ed@example.com")
address2 = Address(email_address="eddy@example.com")
ed_user.addresses = [address, address2]
db.add(ed_user)
db.commit()


def test_defaults() -> None:
    PydanticUser = extract_from_sqlalchemy(User)
    PydanticAddress = extract_from_sqlalchemy(Address)

    class PydanticUserWithAddresses(PydanticUser):
        addresses: List[PydanticAddress] = []

    user = db.query(User).first()
    pydantic_user = PydanticUser.from_orm(user)
    data = pydantic_user.dict()
    assert isinstance(data["created"], datetime)
    assert isinstance(data["updated"], datetime)
    check_data = data.copy()
    del check_data["created"]
    del check_data["updated"]
    assert check_data == {
        "fullname": "Ed Jones",
        "id": 1,
        "name": "ed",
        "nickname": "edsnickname",
    }
    pydantic_user_with_addresses = PydanticUserWithAddresses.from_orm(user)
    data = pydantic_user_with_addresses.dict()
    assert isinstance(data["updated"], datetime)
    assert isinstance(data["created"], datetime)
    check_data = data.copy()
    del check_data["updated"]
    del check_data["created"]
    assert check_data == {
        "fullname": "Ed Jones",
        "id": 1,
        "name": "ed",
        "nickname": "edsnickname",
        "addresses": [
            {"email_address": "ed@example.com", "id": 1, "user_id": 1},
            {"email_address": "eddy@example.com", "id": 2, "user_id": 1},
        ],
    }


def test_schema() -> None:
    PydanticUser = extract_from_sqlalchemy(User)
    PydanticAddress = extract_from_sqlalchemy(Address)
    assert PydanticUser.schema() == {
        "title": "User",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "name": {"title": "Name", "type": "string"},
            "fullname": {"title": "Fullname", "type": "string"},
            "nickname": {"title": "Nickname", "type": "string"},
            "created": {"title": "Created", "type": "string", "format": "date-time"},
            "updated": {"title": "Updated", "type": "string", "format": "date-time"},
        },
        "required": ["id"],
    }
    assert PydanticAddress.schema() == {
        "title": "Address",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "email_address": {"title": "Email Address", "type": "string"},
            "user_id": {"title": "User Id", "type": "integer"},
        },
        "required": ["id", "email_address"],
    }


def test_config() -> None:
    class Config:
        orm_mode = True
        allow_population_by_field_name = True

        @classmethod
        def alias_generator(cls, string: str) -> str:
            pascal_case = "".join(word.capitalize() for word in string.split("_"))
            camel_case = pascal_case[0].lower() + pascal_case[1:]
            return camel_case

    PydanticUser = extract_from_sqlalchemy(User)
    PydanticAddress = extract_from_sqlalchemy(Address, config=Config)

    class PydanticUserWithAddresses(PydanticUser):
        addresses: List[PydanticAddress] = []

    user = db.query(User).first()
    pydantic_user_with_addresses = PydanticUserWithAddresses.from_orm(user)
    data = pydantic_user_with_addresses.dict(by_alias=True)
    assert isinstance(data["created"], datetime)
    assert isinstance(data["updated"], datetime)
    check_data = data.copy()
    del check_data["created"]
    del check_data["updated"]
    assert check_data == {
        "fullname": "Ed Jones",
        "id": 1,
        "name": "ed",
        "nickname": "edsnickname",
        "addresses": [
            {"emailAddress": "ed@example.com", "id": 1, "userId": 1},
            {"emailAddress": "eddy@example.com", "id": 2, "userId": 1},
        ],
    }


def test_exclude() -> None:
    PydanticUser = extract_from_sqlalchemy(User, exclude={"nickname"})
    PydanticAddress = extract_from_sqlalchemy(Address, exclude={"user_id"})

    class PydanticUserWithAddresses(PydanticUser):
        addresses: List[PydanticAddress] = []

    user = db.query(User).first()
    pydantic_user_with_addresses = PydanticUserWithAddresses.from_orm(user)
    data = pydantic_user_with_addresses.dict(by_alias=True)
    assert isinstance(data["created"], datetime)
    assert isinstance(data["updated"], datetime)
    check_data = data.copy()
    del check_data["created"]
    del check_data["updated"]
    assert check_data == {
        "fullname": "Ed Jones",
        "id": 1,
        "name": "ed",
        "addresses": [
            {"email_address": "ed@example.com", "id": 1},
            {"email_address": "eddy@example.com", "id": 2},
        ],
    }
