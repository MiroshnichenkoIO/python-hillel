"""Крок 3: CRUD через Session — серце уроку.

Session — це «робочий стіл»: об'єкти на ньому SQLAlchemy відстежує і при
`commit()` сама пише в базу тільки те, що змінилось. SQL ми не пишемо.

    Create  → session.add(obj) + commit
    Read    → session.get(Model, id)  /  session.scalars(select(Model))
    Update  → змінити атрибут + commit
    Delete  → session.delete(obj) + commit

Запуск (після step_02):
    python step_03_crud_session.py
"""

from decimal import Decimal

from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import SessionLocal, engine
from models import Author, Book


def reset() -> None:
    """Очищає таблиці, щоб кожен запуск починався з нуля."""
    with engine.begin() as connection:
        connection.execute(
            text("TRUNCATE order_items, orders, books, authors RESTART IDENTITY")
        )


def create(session: Session) -> None:
    """C — створюємо об'єкти, як звичайні Python-об'єкти."""
    shevchenko = Author(name="Тарас Шевченко", country="Україна")
    orwell = Author(name="George Orwell", country="UK")
    kobzar = Book(title="Кобзар", price=Decimal("250.00"), stock=5,
                  author=shevchenko)
    session.add_all([shevchenko, orwell, kobzar])

    print("До commit — id ще немає:", kobzar.id, shevchenko.id)
    session.flush()
    print("Після flush — база видала id:", kobzar.id, shevchenko.id)
    session.commit()
    print("Після commit — збережено.")
    print()


def read(session: Session) -> None:
    """R — три способи прочитати."""
    book = session.get(Book, 1)
    print("get за первинним ключем:", book)
    print("  і одразу автор через зв'язок:", book.author.name)

    missing = session.get(Book, 999)
    print("get неіснуючого — не помилка, а:", missing)

    statement = select(Author).where(Author.country == "Україна")
    authors = session.scalars(statement).all()
    print("select з умовою:", authors)

    query = select(Book).order_by(Book.price.desc()).limit(10)
    print("Що піде в базу:")
    print(" ", str(query).replace("\n", "\n  "))
    print()


def update(session: Session) -> None:
    """U — просто змінюємо атрибут; SQLAlchemy сама помічає."""
    book = session.get(Book, 1)
    book.price = Decimal("275.00")
    book.stock -= 1
    print("Session бачить зміни:", session.dirty)
    session.commit()

    session.expire_all()
    fresh = session.get(Book, 1)
    print("Перечитано з бази:", fresh.title, fresh.price, fresh.stock)
    print()


def delete(session: Session) -> None:
    """D — позначаємо на видалення, commit виконує DELETE."""
    orwell = session.scalar(select(Author).where(Author.name == "George Orwell"))
    session.delete(orwell)
    print("Позначено на видалення:", session.deleted)
    session.commit()
    print("Авторів залишилось:", session.scalars(select(Author)).all())
    print()


def rollback_demo(session: Session) -> None:
    """Обмеження бази ловимо як IntegrityError, а сесію повертаємо в лад."""
    book = session.get(Book, 1)
    book.stock = -10
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        print("База відмовила:", error.orig.diag.message_primary)
    print("Після rollback у сесії знову правда:", session.get(Book, 1).stock)
    print()


def main() -> None:
    """Проганяє всі чотири літери CRUD плюс відкат."""
    reset()
    with SessionLocal() as session:
        create(session)
        read(session)
        update(session)
        delete(session)
        rollback_demo(session)


if __name__ == "__main__":
    main()
