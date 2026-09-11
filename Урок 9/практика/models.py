"""Моделі книгарні: Python-класи, які SQLAlchemy перетворює на таблиці.

Кожен клас — таблиця, кожен `Mapped[...]`-атрибут — колонка. Це той самий
`CREATE TABLE` з уроку 8, тільки записаний мовою Python, щоб з ним могли
працювати IDE, перевірка типів і сама програма.
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base


class Author(Base):
    """Автор. Один автор — багато книг (1:N)."""

    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    country: Mapped[str | None] = mapped_column(String(50))

    books: Mapped[list["Book"]] = relationship(back_populates="author")

    def __repr__(self) -> str:
        return f"Author(id={self.id}, name={self.name!r})"


class Book(Base):
    """Книга. Належить одному авторові, може бути в багатьох замовленнях."""

    __tablename__ = "books"
    __table_args__ = (CheckConstraint("stock >= 0", name="stock_not_negative"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    stock: Mapped[int] = mapped_column(default=0)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))

    author: Mapped["Author"] = relationship(back_populates="books")
    order_items: Mapped[list["OrderItem"]] = relationship(
        back_populates="book"
    )

    def __repr__(self) -> str:
        return f"Book(id={self.id}, title={self.title!r}, stock={self.stock})"


class Order(Base):
    """Замовлення — «шапка»: хто і коли. Позиції — в OrderItem."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Order(id={self.id}, customer={self.customer!r})"


class OrderItem(Base):
    """Позиція замовлення — «таблична частина»: яка книга і скільки."""

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    quantity: Mapped[int] = mapped_column(default=1)

    order: Mapped["Order"] = relationship(back_populates="items")
    book: Mapped["Book"] = relationship(back_populates="order_items")

    def __repr__(self) -> str:
        return f"OrderItem(book_id={self.book_id}, quantity={self.quantity})"
