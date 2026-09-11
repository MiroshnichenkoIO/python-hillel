"""Крок 1: Engine і сирий SQL через SQLAlchemy Core.

Ще не ORM. Показуємо, що SQLAlchemy на нижньому рівні — це той самий
`psycopg` з уроку 8, тільки з єдиним рядком підключення, пулом з'єднань
і параметрами у вигляді `:name` замість `%s`.

Працює з базою `shop` з уроку 8 — нічого не змінює, лише читає.

Запуск:
    python step_01_engine_and_text.py
"""

from sqlalchemy import create_engine, text

LESSON_8_URL = "postgresql+psycopg://postgres:secret@127.0.0.1:5432/shop"


def main() -> None:
    """Підключається, читає книги, показує параметри й форми результату."""
    engine = create_engine(LESSON_8_URL, echo=True)
    print("Engine створено, але з'єднань ще немає:", engine.pool.status())
    print()

    with engine.connect() as connection:
        version = connection.execute(text("SELECT version()")).scalar()
        print("Сервер:", version.split(",")[0])
        print()

        result = connection.execute(
            text("SELECT id, title, price FROM books WHERE price > :limit"),
            {"limit": 300},
        )
        print("Колонки результату:", result.keys())
        for row in result:
            print(f"  {row.id}. {row.title:<20} {row.price}")
        print()

        one = connection.execute(
            text("SELECT * FROM books WHERE id = :id"), {"id": 1}
        ).one()
        print("Кортеж:", tuple(one))
        print("За іменем:", one.title, one.price)
        print("Словник:", one._asdict())
        print()

    print("Після виходу з with з'єднання повернулось у пул:")
    print(" ", engine.pool.status())


if __name__ == "__main__":
    main()
