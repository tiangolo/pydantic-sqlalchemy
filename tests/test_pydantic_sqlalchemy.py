from datetime import datetime, timezone
from typing import List

from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker
from sqlalchemy_utc import UtcDateTime

Base = declarative_base()

engine = create_engine("sqlite://", echo=True)


def utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(UtcDateTime, default=utc_now, onupdate=utc_now)

    addresses = relationship(
        "Address", back_populates="user", cascade="all, delete, delete-orphan"
    )
    orders = relationship(
        "Order", back_populates="user", cascade="all, delete, delete-orphan"
    )


class Address(Base):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="addresses")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    address_id = Column(Integer, ForeignKey("addresses.id"))
    description = Column(
        String(100),
        pydantic_description="This description describes description field",
        pydantic_max_length=100,
    )
    quantity = Column(Integer, pydantic_gt=1, pydantic_le=100)
    total = Column(Integer, pydantic_ge=0)

    user = relationship("User", back_populates="orders")
    address = relationship("User", back_populates="orders")


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
    PydanticUser = sqlalchemy_to_pydantic(User)
    PydanticAddress = sqlalchemy_to_pydantic(Address)

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
    PydanticUser = sqlalchemy_to_pydantic(User)
    PydanticAddress = sqlalchemy_to_pydantic(Address)
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

    PydanticUser = sqlalchemy_to_pydantic(User)
    PydanticAddress = sqlalchemy_to_pydantic(Address, config=Config)

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
    PydanticUser = sqlalchemy_to_pydantic(User, exclude={"nickname"})
    PydanticAddress = sqlalchemy_to_pydantic(Address, exclude={"user_id"})

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


def test_custom_arguments() -> None:
    PydanticOrder = sqlalchemy_to_pydantic(Order, exclude={"user_id", "address_id"})
    assert PydanticOrder.schema()["properties"] == {
        "id": {"title": "Id", "type": "integer"},
        "description": {
            "title": "Description",
            "description": "This description describes description field",
            "maxLength": 100,
            "type": "string",
        },
        "quantity": {
            "title": "Quantity",
            "exclusiveMinimum": 1,
            "maximum": 100,
            "type": "integer",
        },
        "total": {"title": "Total", "minimum": 0, "type": "integer"},
    }
