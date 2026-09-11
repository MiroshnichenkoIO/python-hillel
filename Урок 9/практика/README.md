# Практика уроку 9 — CRUD із SQLAlchemy 2 + PostgreSQL

Усе працює на **живому PostgreSQL 16 у Docker** (контейнер `pg-lesson8` з
уроку 8). Крок 1 читає базу `shop` з уроку 8, решта кроків працюють у
власній базі `shop_orm`, яку крок 2 створює сам.

## Файли

| Файл | Про що |
|---|---|
| `db.py` | рядок підключення, `engine`, `SessionLocal`, `Base`, створення бази |
| `models.py` | моделі: `Author` 1:N `Book`, `Order` 1:N `OrderItem` N:1 `Book` |
| `step_01_engine_and_text.py` | Engine, пул, `text()` з параметрами `:name`, `Row` |
| `step_02_models_and_tables.py` | з класів — таблиці: DDL, `create_all`, `inspect` |
| `step_03_crud_session.py` | Session: add / get / select / зміна / delete / rollback |
| `step_04_relationships.py` | зв'язки, lazy loading, проблема N+1, `selectinload`, каскад |
| `step_05_fastapi_crud.py` | той самий CRUD через FastAPI: `Depends`, `from_attributes` |
| `alembic_demo/` | мінімальний Alembic на SQLite: дві міграції, `upgrade`/`downgrade` |
| `bookshop/` | **проєкт за викладачем**: `User`/`Post`, `crud.py`, `main.py`-сценарій, Alembic на `shop_db` (див. конспект, розділ 13) |

## Підготовка

```bash
docker start pg-lesson8            # якщо контейнер зупинений
pip install "sqlalchemy>=2" "psycopg[binary]"
```

## Запуск

```bash
cd "d:\PY\Урок 9\практика"

python step_01_engine_and_text.py       # читає базу уроку 8
python step_02_models_and_tables.py     # створює shop_orm і таблиці
python step_03_crud_session.py
python step_04_relationships.py

uvicorn step_05_fastapi_crud:app --reload --port 8011
# http://127.0.0.1:8011/docs

cd bookshop
python main.py                          # сценарій викладача (create → … → delete)
uvicorn api:app --reload --port 8012    # той самий crud через FastAPI
alembic revision --autogenerate -m "..." ; alembic upgrade head   # після зміни models.py
```

Кроки 3 і 4 самі очищають таблиці на старті (`TRUNCATE ... RESTART
IDENTITY`), тому порядок і кількість запусків не важливі. Крок 5 працює з
тим, що залишив крок 4.

## Подивитись базу очима

pgAdmin — `http://localhost:5050`, сервер «Урок 8», тепер там дві бази:
`shop` (урок 8) і `shop_orm` (цей урок).
