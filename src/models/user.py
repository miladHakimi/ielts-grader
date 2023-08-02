import datetime

from typing import Optional, List
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from sqlalchemy.types import DateTime, Float, Integer, String

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    username: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    start_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    expiry_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    num_requests: Mapped[int] = mapped_column(Integer, default=0)
    balance = mapped_column(Float, default=0.0)
    words: Mapped[List["Word"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, num_requests={self.num_requests}, expiry_time={self.expiry_time})"
