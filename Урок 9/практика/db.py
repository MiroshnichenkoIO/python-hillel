"""Спільне для всіх кроків: рядок підключення, engine, фабрика сесій, Base.

Ідея та сама, що в `db.py` з уроку 8: одне місце, де описано, ЯК ми
підключаємось, щоб решта файлів імпортувала готове й не повторювала пароль.

Запуск напряму створює базу `shop_orm` на сервері, якщо її ще немає:
    python db.py
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SERVER_URL = "postgresql+psycopg://postgres:secret@127.0.0.1:5432"
DATABASE_NAME = "shop_orm"
DATABASE_URL = f"{SERVER_URL}/{DATABASE_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    """Спільний предок усіх моделей: збирає в собі опис таблиць (metadata)."""


def ensure_database() -> None:
    """Створює базу `shop_orm`, якщо на сервері її ще немає.

    `CREATE DATABASE` не можна виконати всередині транзакції, тому
    підключаємось до службової бази `postgres` у режимі AUTOCOMMIT.
    """
    admin_engine = create_engine(
        f"{SERVER_URL}/postgres", isolation_level="AUTOCOMMIT"
    )
    with admin_engine.connect() as connection:
        exists = connection.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": DATABASE_NAME},
        ).scalar()
        if not exists:
            connection.execute(text(f'CREATE DATABASE "{DATABASE_NAME}"'))
            print(f"Базу {DATABASE_NAME} створено.")
        else:
            print(f"База {DATABASE_NAME} уже є.")
    admin_engine.dispose()


if __name__ == "__main__":
    ensure_database()
