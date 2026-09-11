"""Крок 2: з класів — таблиці.

`Base.metadata` знає всі класи, що успадкували `Base`. `create_all` дивиться,
яких таблиць у базі немає, і виконує для них `CREATE TABLE`. Той, що є, не
чіпає — тому міняти колонки через `create_all` не вийде (для цього Alembic).

Запуск:
    python step_02_models_and_tables.py
"""

from sqlalchemy import inspect
from sqlalchemy.schema import CreateTable

from db import Base, engine, ensure_database
from models import Author, Book, Order, OrderItem


def show_ddl() -> None:
    """Друкує SQL, який SQLAlchemy згенерує з наших класів."""
    for model in (Author, Book, Order, OrderItem):
        print(CreateTable(model.__table__).compile(engine))


def show_tables() -> None:
    """Питає у самої бази, які таблиці й колонки в ній є."""
    inspector = inspect(engine)
    for table in inspector.get_table_names():
        columns = ", ".join(
            f"{column['name']}:{column['type']}"
            for column in inspector.get_columns(table)
        )
        print(f"  {table}: {columns}")


def main() -> None:
    """Створює базу і таблиці, показує DDL і те, що реально вийшло."""
    ensure_database()
    print()

    print("Що SQLAlchemy збирається виконати:")
    show_ddl()

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("Таблиці створено. Що каже база:")
    show_tables()
    print()

    print("Таблиці, які знає Base.metadata:", list(Base.metadata.tables))
    print("Повторний create_all нічого не зламає — він пропускає наявні.")
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    main()
