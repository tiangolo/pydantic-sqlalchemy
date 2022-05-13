from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from tests.fixtures.Base import Base
from tests.fixtures.Point import Point


class Address(Base):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    coordinated = Column(Point(), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="addresses")
