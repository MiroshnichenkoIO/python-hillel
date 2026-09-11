"""Модель для демонстрації Alembic. Спочатку — тільки id і title."""

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Реєстр таблиць, з яким Alembic порівнює базу."""


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    year: Mapped[int | None]
