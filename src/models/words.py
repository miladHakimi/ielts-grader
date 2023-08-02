import datetime

from . import User, Base

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime, Integer, String


class Word(Base):
    __tablename__ = 'word_table'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    word: Mapped[str] = mapped_column(String(50), nullable=False)
    correct_guesses: Mapped[int] = mapped_column(Integer, default=0)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    last_used: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    user: Mapped["User"] = relationship(back_populates="words")
    __table_args__ = (UniqueConstraint('word', 'user_id', name='unique_word_user_id'), )

    def __repr__(self):
        return f"word={self.word}, correct_guesses={self.correct_guesses}, user_id={self.user_id}, last_used={self.last_used})"
