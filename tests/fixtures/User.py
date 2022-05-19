from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from sqlalchemy_utc import UtcDateTime

from tests.fixtures.Base import Base, utc_now


class User(Base):
    __tablename__ = "users"
    STATES = ["active", "inactive", "banned", "deleted"]
    id = Column(Integer, primary_key=True)
    status = Column(Enum(*STATES), default="daily", nullable=False)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(UtcDateTime, default=utc_now, onupdate=utc_now)
    due_date = Column(Date(), nullable=False)

    addresses = relationship(
        "Address", back_populates="user", cascade="all, delete, delete-orphan"
    )

    following = relationship(
        'User',
        lambda: user_following,
        primaryjoin=lambda: User.id == user_following.c.user_id,
        secondaryjoin=lambda: User.id == user_following.c.following_id,
        backref='followers'
    )

user_following = Table(
    'user_following', Base.metadata,
    Column('user_id', Integer, ForeignKey(User.id), primary_key=True),
    Column('following_id', Integer, ForeignKey(User.id), primary_key=True)
)