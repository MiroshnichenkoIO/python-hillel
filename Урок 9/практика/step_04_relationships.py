"""Крок 4: зв'язки, ліниве завантаження і проблема N+1.

`relationship` — це JOIN, який робиться сам. Але «сам» означає: у момент,
коли ми вперше торкнулись атрибута. Для списку з 100 книг це 100 запитів.
Ліки — сказати заздалегідь, що нам буде потрібно: `selectinload`.

Запуск (після step_02):
    python step_04_relationships.py
"""

import logging
from decimal import Decimal

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session, selectinload

from db import SessionLocal, engine
from models import Author, Book, Order, OrderItem


class QueryCounter(logging.Handler):
    """Рахує SQL-запити, які Engine відправляє в базу."""

    def __init__(self) -> None:
        super().__init__()
        self.count = 0

    def emit(self, record: logging.LogRecord) -> None:
        if record.getMessage().lstrip().upper().startswith(("SELECT", "INSERT")):
            self.count += 1


def seed(session: Session) -> None:
    """Наповнює базу: 3 автори, 6 книг, 2 замовлення."""
    with engine.begin() as connection:
        connection.execute(
            text("TRUNCATE order_items, orders, books, authors RESTART IDENTITY")
        )
    shevchenko = Author(name="Тарас Шевченко", country="Україна")
    orwell = Author(name="George Orwell", country="UK")
    bradbury = Author(name="Ray Bradbury", country="USA")
    books = [
        Book(title="Кобзар", price=Decimal("250"), stock=5, author=shevchenko),
        Book(title="Гайдамаки", price=Decimal("180"), stock=3,
             author=shevchenko),
        Book(title="1984", price=Decimal("410"), stock=7, author=orwell),
        Book(title="Animal Farm", price=Decimal("290"), stock=0,
             author=orwell),
        Book(title="Fahrenheit 451", price=Decimal("350"), stock=4,
             author=bradbury),
        Book(title="The Martian Chronicles", price=Decimal("330"), stock=2,
             author=bradbury),
    ]
    order = Order(customer="Ігор", items=[
        OrderItem(book=books[0], quantity=2),
        OrderItem(book=books[2], quantity=1),
    ])
    session.add_all([shevchenko, orwell, bradbury, *books, order])
    session.commit()


def n_plus_one(session: Session, counter: QueryCounter) -> None:
    """Показує, скільки запитів іде без підказки і з нею."""
    session.expire_all()
    counter.count = 0
    for book in session.scalars(select(Book)):
        _ = book.author.name
    print("Ліниво (lazy): книг 6, запитів у базу —", counter.count)

    session.expire_all()
    counter.count = 0
    statement = select(Book).options(selectinload(Book.author))
    for book in session.scalars(statement):
        _ = book.author.name
    print("З selectinload: запитів у базу —", counter.count)
    print()


def navigate(session: Session) -> None:
    """Ходимо по зв'язках в обидва боки, як по посиланнях у 1С."""
    author = session.scalar(select(Author).where(Author.name.like("%Orwell")))
    print(author.name, "написав:", [book.title for book in author.books])

    order = session.get(Order, 1)
    print(f"Замовлення {order.id} від {order.customer!r}:")
    for item in order.items:
        print(f"  {item.book.title:<12} x{item.quantity} "
              f"= {item.book.price * item.quantity}")
    print()


def join_and_aggregate(session: Session) -> None:
    """Той самий GROUP BY з уроку 8, але записаний Python-виразами."""
    statement = (
        select(Author.name, func.count(Book.id), func.sum(Book.stock))
        .join(Author.books)
        .group_by(Author.name)
        .order_by(func.count(Book.id).desc())
    )
    print("Автор → книг, залишок:")
    for name, count, stock in session.execute(statement):
        print(f"  {name:<16} {count} книг, залишок {stock}")
    print()


def cascade_demo(session: Session) -> None:
    """Видаляємо замовлення — позиції зникають самі (cascade)."""
    order = session.get(Order, 1)
    session.delete(order)
    session.commit()
    left = session.scalar(select(func.count()).select_from(OrderItem))
    print("Видалили замовлення; позицій залишилось:", left)


def main() -> None:
    """Сід, N+1, навігація по зв'язках, агрегати, каскад."""
    counter = QueryCounter()
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").addHandler(counter)

    with SessionLocal() as session:
        seed(session)
        n_plus_one(session, counter)
        navigate(session)
        join_and_aggregate(session)
        cascade_demo(session)


if __name__ == "__main__":
    main()
