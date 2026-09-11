# Урок 9 — CRUD із SQLAlchemy 2 + PostgreSQL

Конспект розібраного. Поповнюється по ходу заняття.

---

## 0. Повторення уроку 8

### Що потрібно пам'ятати

**Три головні думки уроку 8.** База — це не «файл із даними», а движок,
який тримає структуру, перевіряє обмеження і сам вирішує, *як* знайти
рядок; SQL — мова, якою ми описуємо *що* нам треба; і все, чого не
оголосили обмеженнями, база не перевірятиме.

**Мови всередині SQL.** DDL (`CREATE`/`ALTER`/`DROP` — креслення), DML
(`INSERT`/`UPDATE`/`DELETE` — рядки), DQL (`SELECT` — половина уроку), TCL
(`BEGIN`/`COMMIT`/`ROLLBACK`), DCL (`GRANT`). У 1С DDL робить конфігуратор
із метаданих, тут — ми самі.

**Ключі та зв'язки.** `PRIMARY KEY` — адреса рядка (у нас сурогатний
`id`, у 1С — GUID-посилання); `FOREIGN KEY` — обмеження, яке не дає
«висячих» посилань, і його треба написати руками. 1:N — зовнішній ключ у
«багатьох»; M:N — окрема таблиця-зв'язка. Таблична частина 1С = окрема
таблиця з `FOREIGN KEY` на «шапку».

**`SELECT`.** Порядок написання `SELECT → FROM → WHERE → GROUP BY → HAVING
→ ORDER BY → LIMIT`, порядок виконання інший: спочатку `FROM`, наприкінці
`SELECT` і `LIMIT`. `WHERE` фільтрує рядки до групування, `HAVING` — групи
після. `JOIN` збирає назад те, що розклала нормалізація; `LEFT JOIN`
зберігає рядки без пари; `UNION` складає результати вертикально —
не плутати з `JOIN`.

**Транзакція.** Кілька змін як одне ціле: або всі, або жодна (ACID).
У DB-API транзакція відкривається неявно і висить до `commit()`; забув —
втратив дані. `with connection:` у `sqlite3` робить commit/rollback, але
**не закриває** з'єднання.

**Нормалізація.** 1НФ — атомарні значення, без списків у комірці; 2НФ —
усе залежить від *усього* ключа; 3НФ — нічого не залежить від неключових
колонок. Ліки від трьох аномалій: вставки, оновлення, видалення.
Денормалізують свідомо і задокументовано.

**Індекси.** Окрема структура (B-tree за замовчуванням), яка обмінює місце
і швидкість запису на швидкість пошуку. Зовнішні ключі в PostgreSQL
індексуються **вручну**. Часткові, функціональні, `INCLUDE`.

**SQL із Python.** `sqlite3` в стандартній бібліотеці, `psycopg2` для
PostgreSQL. Параметри — тільки через `?` / `%s`, ніколи через f-рядок:
склеювання тексту запиту з даними = SQL-ін'єкція. `row_factory =
sqlite3.Row` вмикає доступ за іменем.

**PostgreSQL проти SQLite.** Сервер проти файлу; `SERIAL`/`IDENTITY`
проти `INTEGER PRIMARY KEY`; `%s` проти `?`; типи перевіряються строго;
`RETURNING` є в обох. У нас PostgreSQL 16 живе в Docker (`pg-lesson8`),
pgAdmin — `http://localhost:5050`.

### Питання для самоперевірки

1. Чим сурогатний ключ відрізняється від природного і чому ми обрали
   перший?
2. Чому `WHERE stock > 0` не можна замінити на `HAVING stock > 0` і навпаки
   `HAVING COUNT(*) > 1` на `WHERE`?
3. Що поверне `LEFT JOIN`, чого не поверне `INNER JOIN`?
4. Таблиця `orders(id, customer_name, customer_phone, book_title, price)`
   — яку нормальну форму вона порушує і чим це загрожує?
5. Чому `cursor.execute(f"... WHERE id = {user_input}")` — це дірка, а
   `cursor.execute("... WHERE id = %s", (user_input,))` — ні?
6. Що станеться з даними, якщо після трьох `INSERT` процес упаде до
   `commit()`?
7. Індекс на `books(author_id)` — навіщо, якщо там і так `FOREIGN KEY`?
8. Чим `docker stop` відрізняється від `docker rm` для наших даних?

### Місток до уроку 9

Урок 8 закінчився запитом-рядком:

```python
connection.execute(
    "SELECT title, price FROM books WHERE id = ?", (book_id,)
).fetchone()
```

І трьома незручностями: помилку в рядку побачить тільки база під час
виконання; з бази приходить кортеж, а у FastAPI потрібна модель; SQL
різних СУБД трохи різний. Плюс четверта, яку ми відчули руками:
**`storage.py` уроку 7 і `db.py` уроку 8 — це два різні світи**, між якими
доводиться переписувати кожен об'єкт у кортеж і назад.

ORM закриває всі чотири: таблиця стає класом, рядок — об'єктом,
`SELECT ... WHERE id = ?` — `session.get(Book, book_id)`, а SQL під різні
СУБД генерує бібліотека. Сьогодні — SQLAlchemy 2, найпоширеніша ORM у
Python, і той самий CRUD, що ми робили в уроках 7 і 8, але третій раз —
уже без рядків SQL і без словників у пам'яті.

---

## 1. Що таке ORM і навіщо

**ORM — Object-Relational Mapping**, «відображення об'єктів на реляційну
базу». Бібліотека, яка тримає таблицю відповідностей:

| У базі | У Python |
|---|---|
| таблиця | клас |
| колонка | атрибут класу |
| рядок | екземпляр (об'єкт) |
| `FOREIGN KEY` | атрибут-посилання на інший об'єкт |
| `INSERT` / `UPDATE` / `DELETE` | `session.add()` / зміна атрибута / `session.delete()` + `commit()` |
| `SELECT` | `session.get()` / `select(Model).where(...)` |

**Аналогія з 1С — найточніша за весь курс.** У 1С ти ніколи не пишеш
`INSERT INTO _Reference37`. Ти робиш `Довідники.Номенклатура.СоздатьЭлемент()`,
заповнюєш реквізити, викликаєш `Записать()` — і платформа сама
перекладає це в SQL для MS SQL чи PostgreSQL. Об'єкт `ДовідникОб'єкт` — це
і є «рядок у вигляді об'єкта». ORM — це той самий шар платформи, тільки
без конфігуратора: класи ти описуєш сам, у коді.

Відмінність, яка ламає звичку: у 1С об'єкт «сам знає», як записатись —
`Записать()` викликається на ньому. У SQLAlchemy об'єкт нічого не знає про
базу; записує **сесія**, на якій цей об'єкт лежить. Про це весь розділ 4.

### Три поверхи SQLAlchemy

SQLAlchemy — не лише ORM. Це три шари, і на кожному можна зупинитись:

```
   ORM         Session, моделі-класи, relationship        ← розділи 3–6
   Core        Engine, text(), select(), Table, MetaData  ← розділ 2
   DBAPI       psycopg / psycopg2 / sqlite3                ← урок 8
```

* **DBAPI** — драйвер, той самий `psycopg2` з уроку 8. SQLAlchemy його не
  замінює, а сідає зверху.
* **Core** — «SQL мовою Python»: `select(books).where(books.c.price > 300)`
  збирає SQL-вираз, який бібліотека перекладе в діалект потрібної СУБД.
  Об'єктів немає, є таблиці й рядки.
* **ORM** — класи та сесія поверх Core.

Ми пройдемо всі три знизу вгору, бо кожен вищий поверх пояснюється через
нижчий.

---

## 2. Підключення: Engine, пул, `text()`

### Установка

```bash
pip install "sqlalchemy>=2" "psycopg[binary]"
```

`psycopg` (без цифри) — це **psycopg 3**, сучасний драйвер PostgreSQL;
`psycopg2` з уроку 8 теж працює, але у SQLAlchemy 2 рекомендують третій.
`[binary]` — зібраний пакет, не треба компілятора. У нас стоїть
SQLAlchemy 2.0.52 і psycopg 3.3.5 в обох venv.

### Рядок підключення (URL)

```python
"postgresql+psycopg://postgres:secret@127.0.0.1:5432/shop"
 └────┬───┘ └──┬──┘   └──┬───┘ └─┬──┘ └───┬───┘ └┬─┘ └┬─┘
   діалект   драйвер    user   пароль   host    порт  база
```

Замість чотирьох параметрів `psycopg2.connect(host=..., port=..., ...)` —
один рядок, як адреса сайту. Змінити базу — змінити один рядок; для SQLite
буде `sqlite:///shop.db`, для MySQL — `mysql+pymysql://...`. Це і є
«SQL різних СУБД» з мостика: різниця сховалась у діалект.

### Engine — не з'єднання, а фабрика з'єднань

```python
from sqlalchemy import create_engine, text

engine = create_engine(URL, echo=True)
```

`create_engine` **не підключається** до бази. Він запам'ятовує URL і
створює **пул** — резерв з'єднань, які відкриваються на першу вимогу і
потім повертаються назад, а не закриваються. З `step_01`:

```
Engine створено, але з'єднань ще немає: Pool size: 5  Connections in pool: 0
...
Після виходу з with з'єднання повернулось у пул:
  Pool size: 5  Connections in pool: 1
```

Навіщо пул: відкрити TCP-з'єднання з PostgreSQL і пройти автентифікацію —
десятки мілісекунд. Для API з сотнею запитів на секунду це неприйнятно;
пул дає готове з'єднання за мікросекунди. У 1С аналог — з'єднання, яке
тримає сервер 1С з SQL Server від імені всіх сеансів.

`echo=True` друкує кожен SQL, який іде в базу — найкращий спосіб зрозуміти,
що ORM робить під капотом. У бою вимикають.

### `connect()` проти `begin()`

```python
with engine.connect() as connection:       # транзакція відкрита неявно,
    connection.execute(text("..."))        # у кінці — ROLLBACK
    connection.commit()                    # якщо треба зберегти — явно

with engine.begin() as connection:         # у кінці — COMMIT
    connection.execute(text("..."))        # (або ROLLBACK при винятку)
```

У логу `step_01` видно: `BEGIN (implicit)` на початку і `ROLLBACK` у кінці
`with engine.connect()`. Це **навмисне**: SQLAlchemy 2 ніколи не комітить
сама — «commit as you go». Для читання неважливо, для запису через
`connect()` треба `connection.commit()`, інакше все відкотиться. Для
коротких сценаріїв «зробив і зберіг» бери `engine.begin()` — це аналог
`with connection:` із `sqlite3`.

### `text()` і параметри

```python
result = connection.execute(
    text("SELECT id, title, price FROM books WHERE price > :limit"),
    {"limit": 300},
)
```

* `text()` — обгортка «це сирий SQL, я знаю, що роблю». Без неї
  `execute("рядок")` у SQLAlchemy 2 кине помилку — навмисно, щоб не
  провокувати конкатенацію.
* Параметр — `:limit`, значення — словник. Один синтаксис для всіх СУБД;
  у лог пішло `WHERE price > %(limit)s {'limit': 300}` — SQLAlchemy сама
  переклала `:limit` у стиль psycopg. Це та сама захист від ін'єкцій
  з уроку 8, тільки з іменами замість позицій.

### `Row` — рядок з іменами

```
Кортеж:    (1, 'Кобзар', 1, 1840, Decimal('250.00'), 12)
За іменем: Кобзар 250.00       ← row.title, row.price
Словник:   {'id': 1, 'title': 'Кобзар', ...}   ← row._asdict()
```

`Row` — як `sqlite3.Row` з уроку 8, але за замовчуванням і з доступом
через крапку. Методи результату:

| Метод | Повертає |
|---|---|
| `result.all()` | список `Row` |
| `result.first()` | перший `Row` або `None` |
| `result.one()` | рівно один `Row`, інакше виняток |
| `result.scalar()` | перше значення першого рядка (`SELECT count(*)`) |
| `result.scalars()` | перша колонка кожного рядка |
| `result.keys()` | імена колонок |
| `for row in result` | ітерація |

`price` прийшла як `Decimal` — тип `NUMERIC(10, 2)` з уроку 8 дійшов до
Python без втрат; `float` тут був би помилкою для грошей.

---

## 3. Моделі: клас = таблиця

### Declarative — новий синтаксис SQLAlchemy 2

```python
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Спільний предок усіх моделей."""


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    stock: Mapped[int] = mapped_column(default=0)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
```

Розбираємо рядок за рядком.

**`class Base(DeclarativeBase)`.** Один на проєкт. Усе, що успадкує `Base`,
потрапляє в `Base.metadata` — реєстр таблиць. Це те саме, що в 1С «дерево
конфігурації»: список усіх об'єктів, з якого платформа знає, які таблиці
створити.

**`__tablename__`** — ім'я таблиці в базі. Клас — однина (`Book`), таблиця
— множина (`books`): звична домовленість.

**`Mapped[int]`** — анотація типу. Це те, за що ми полюбили FastAPI в
уроці 7: анотація не коментар, а працююча інформація. SQLAlchemy читає її
і сама вибирає тип колонки:

| Анотація | Колонка PostgreSQL |
|---|---|
| `Mapped[int]` | `INTEGER` |
| `Mapped[str]` | `VARCHAR` (без довжини — `TEXT`) |
| `Mapped[Decimal]` | `NUMERIC` |
| `Mapped[bool]` | `BOOLEAN` |
| `Mapped[datetime]` | `TIMESTAMP` |
| `Mapped[str \| None]` | `VARCHAR` **NULL** |
| `Mapped[str]` | `VARCHAR` **NOT NULL** |

Останні два — важливі: **обов'язковість колонки випливає з анотації**.
`Mapped[str]` дає `NOT NULL`, `Mapped[str | None]` — дозволяє `NULL`. Не
треба писати `nullable=False` руками — і IDE одночасно знає, що
`book.title` ніколи не буде `None`.

**`mapped_column(...)`** — уточнення, які з анотації не виводяться:
`primary_key=True`, `String(200)` (довжина), `Numeric(10, 2)` (точність),
`default=0`, `ForeignKey("authors.id")`, `unique=True`, `index=True`. Якщо
уточнень немає, `mapped_column()` можна опустити зовсім — `name: Mapped[str]`
теж працює.

**`default` проти `server_default`.**

```python
stock: Mapped[int] = mapped_column(default=0)                  # Python
created_at: Mapped[datetime] = mapped_column(server_default=func.now())  # база
```

`default` підставляє SQLAlchemy на боці Python перед `INSERT`; у DDL його
не буде. `server_default` іде в `CREATE TABLE` як `DEFAULT now()` — його
побачить і pgAdmin, і будь-який інший клієнт бази. Для «час створення»
завжди `server_default`: годинник бази один, а серверів Python може бути
багато.

**`__table_args__`** — те, що стосується таблиці, а не однієї колонки:

```python
__table_args__ = (CheckConstraint("stock >= 0", name="stock_not_negative"),)
```

Кома в кінці обов'язкова — це має бути кортеж. `CheckConstraint` з уроку
8 нікуди не подівся: ORM не скасовує обмежень бази, а лише допомагає їх
оголосити.

### `Base.metadata.create_all()` — від класів до таблиць

```python
Base.metadata.create_all(engine)
```

Обходить усі зареєстровані класи, для кожного питає базу «є така таблиця?»
і виконує `CREATE TABLE` тільки для відсутніх. Що згенерувалось (`step_02`,
через `CreateTable(model.__table__).compile(engine)`):

```sql
CREATE TABLE books (
	id SERIAL NOT NULL,
	title VARCHAR(200) NOT NULL,
	price NUMERIC(10, 2) NOT NULL,
	stock INTEGER NOT NULL,
	author_id INTEGER NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT stock_not_negative CHECK (stock >= 0),
	FOREIGN KEY(author_id) REFERENCES authors (id)
)
```

Це майже дослівно `01_schema_postgres.sql` з уроку 8 — тільки ми його не
писали. Зверни увагу: `id SERIAL` — SQLAlchemy знає діалект PostgreSQL і
сама поставила автоінкремент; для SQLite було б `INTEGER PRIMARY KEY`.

**Ловушка:** `create_all` **не змінює** наявні таблиці. Додав колонку до
класу — у базі вона не з'явиться, і перший же `SELECT` впаде з «column does
not exist». Для еволюції схеми є **Alembic** (міграції) — тема наступного
уроку. На навчанні обходимось `drop_all()` + `create_all()`, як у `step_02`.

### `inspect(engine)` — спитати базу

```python
inspector = inspect(engine)
inspector.get_table_names()          # ['authors', 'books', 'orders', 'order_items']
inspector.get_columns("books")       # [{'name': 'id', 'type': INTEGER(), ...}, ...]
```

Той самий `information_schema` з уроку 8, обгорнутий у методи. Зручно
звірити «що я описав у класах» з «що реально в базі» — якраз для ловушки
вище.

---

## 4. Session — робочий стіл

### Що це

```python
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(bind=engine)

with SessionLocal() as session:
    ...
```

`sessionmaker` — фабрика; `SessionLocal()` — нова сесія. Сесія бере
з'єднання з пулу на першу вимогу і повертає при закритті.

Сесія — це **робочий стіл** (у документації — *unit of work*, «одиниця
роботи»). Ти кладеш на нього об'єкти, змінюєш їх, забираєш — а сесія
записує, що з ними сталося. У момент `commit()` вона дивиться на стіл і
сама вирішує, які `INSERT`/`UPDATE`/`DELETE` і в якому порядку відправити.

Аналогія з 1С — **транзакція проведення документа**: у модулі проведення
ти рухаєш регістри, змінюєш реквізити, і все це або записується разом при
виході, або відкочується цілком.

### Стани об'єкта

Об'єкт відносно сесії буває в одному з п'яти станів:

```
 Book(...)      session.add()       session.flush()/commit()
 transient  ─────────────────▶  pending  ─────────────────▶  persistent
 (просто                        (на столі,                   (є в базі,
  об'єкт)                        ще не в базі)                сесія стежить)
                                                                  │
                                            session.close()       │  session.delete()
                                                                  │  + commit()
                                              detached  ◀─────────┴─────────▶  deleted
```

Це видно в `step_03`:

```
До commit — id ще немає: None None        ← pending: базі ще не казали
Після flush — база видала id: 1 1         ← persistent: INSERT пішов
Після commit — збережено.                 ← транзакція зафіксована
```

### `flush()` проти `commit()`

* **`flush()`** — відправити накопичені зміни в базу **в межах поточної
  транзакції**. Після нього об'єкти мають `id` (база повернула через
  `RETURNING`), але інші з'єднання цього ще не бачать.
* **`commit()`** — `flush()` + `COMMIT`. Зміни стають видимими всім.

Явний `flush()` потрібен рідко — коли `id` треба **до** коміту (наприклад,
щоб вставити його в іншу таблицю). Зазвичай сесія робить `autoflush` сама
перед кожним запитом.

### Що сесія відстежує

```python
book.price = Decimal("275.00")
book.stock -= 1
print(session.dirty)     # IdentitySet([Book(id=1, title='Кобзар', stock=4)])
session.commit()         # → UPDATE books SET price=..., stock=... WHERE id=1
```

Ми не викликали ніякого `save()`. Сесія перехопила присвоєння атрибутів
(через дескриптори — ті самі, що робили `@property` в уроці 4) і помітила
об'єкт як «брудний». `session.new`, `session.dirty`, `session.deleted` —
три списки, з яких `commit()` збирає SQL. У `UPDATE` підуть **тільки
змінені колонки**, а не всі.

### Identity map — один рядок = один об'єкт

Сесія гарантує: в її межах рядку з `id=1` відповідає **рівно один**
Python-об'єкт. Два `session.get(Book, 1)` поспіль повернуть той самий
об'єкт, і другий раз — без запиту в базу. Саме тому в `step_04` «ліниве»
завантаження для 6 книг дало не 7 запитів, а 4: перший — за книгами, і
по одному на кожного з **трьох** авторів; коли друга книга Шевченка
попросила автора, він уже лежав на столі.

### `expire` і `refresh`

Після `commit()` сесія **позначає всі об'єкти застарілими** (expired):
наступне звертання до будь-якого атрибута зробить `SELECT` і перечитає
рядок. Логіка: після коміту базу могли змінити інші, а старе значення в
пам'яті — це брехня. У `step_03` ми зробили це явно:

```python
session.expire_all()
fresh = session.get(Book, 1)    # → SELECT ... WHERE id = 1
```

`session.refresh(obj)` — перечитати один об'єкт негайно. Знадобиться у
FastAPI (розділ 7): після `commit()` віддати клієнту об'єкт із `id` і
`created_at`, які згенерувала база.

### ACID очима сесії

| | Гарантія | У SQLAlchemy |
|---|---|---|
| **A**tomicity | все або нічого | увесь «стіл» іде одним `commit()`; після винятку — `rollback()` |
| **C**onsistency | обмеження не порушуються | `CHECK`/`FOREIGN KEY` → `IntegrityError`, транзакція відхилена цілком |
| **I**solation | інші не бачать півроботи | після `flush()` є `id`, але ззовні рядка не видно до `commit()` |
| **D**urability | після `commit()` — назавжди | `engine.connect()` без `commit()` = `ROLLBACK`; довговічність лише за явним підписом |

Найчастіше ACID ламає не база, а програміст: дві сесії на одну операцію
(«шапка» в одній, позиції в другій). Звідси правило нижче.

### Одна сесія — одна одиниця роботи

Правило: **сесія коротка**. Один HTTP-запит, одна CLI-команда, одна
операція — одна сесія. Не тримати глобальну сесію на все життя програми:
вона накопичує об'єкти, тримає з'єднання і після першої помилки стає
непридатною, поки не зроблено `rollback()`.

---

## 5. CRUD — чотири дії

### Create

```python
shevchenko = Author(name="Тарас Шевченко", country="Україна")
kobzar = Book(title="Кобзар", price=Decimal("250.00"), stock=5,
              author=shevchenko)
session.add_all([shevchenko, kobzar])
session.commit()
```

* Конструктор моделі приймає всі колонки як іменовані аргументи — його
  написав `DeclarativeBase`, не ми.
* `author=shevchenko` — ми передали **об'єкт**, а не `author_id=1`. Id у
  Шевченка ще немає — він з'явиться після `flush`, і SQLAlchemy сама
  спочатку вставить автора, потім підставить його `id` у книгу. Порядок
  `INSERT` вона визначає за зовнішніми ключами.
* `add()` — один об'єкт, `add_all()` — список.

**Ловушка порядку `id`.** `add_all` **каскадно** обходить усі зв'язані
об'єкти в глибину: поклав Шевченка → сесія побачила його `books` → у
«Кобзаря» побачила `order_items` → там `order` → у ньому другу позицію →
«1984» → Орвелла → «Animal Farm» → і лише потім повернулась до
«Гайдамаків». У `step_04` це дало `id`: Кобзар=1, 1984=2, Animal Farm=3,
Гайдамаки=4. Порядок `id` ≠ порядок у списку. Якщо він важливий — окремі
`add()` + `flush()`.

### Read

Три інструменти під три задачі:

```python
# 1. За первинним ключем — найшвидше, identity map, без SQL якщо вже є
book = session.get(Book, 1)          # Book або None — не виняток!

# 2. Вибірка об'єктів
statement = select(Author).where(Author.country == "Україна")
authors = session.scalars(statement).all()      # list[Author]
one = session.scalar(statement)                 # перший або None

# 3. Вибірка колонок / агрегатів — рядки, не об'єкти
rows = session.execute(select(Book.title, Book.price)).all()   # list[Row]
```

**`select()` — це вираз, а не запит.** Він нічого не виконує, а збирає
дерево SQL-виразу, яке можна друкувати:

```
SELECT books.id, books.title, books.price, books.stock, books.author_id
FROM books ORDER BY books.price DESC
 LIMIT :param_1
```

Усі частини уроку 8 є як методи: `.where()`, `.order_by()`, `.limit()`,
`.offset()`, `.join()`, `.group_by()`, `.having()`, `.distinct()`.
Умови — звичайні Python-оператори над атрибутами класу: `Book.price > 300`,
`Author.name.like("%Orwell")`, `Book.stock.in_([0, 1])`, `Book.author_id
.is_(None)`. Клас `Book` тут виступає не як об'єкт, а як **опис колонок** —
тому `Book.price > 300` повертає не `bool`, а SQL-вираз.

**`scalars()` проти `execute()`.** `execute()` завжди повертає рядки
(`Row`), навіть якщо в `select` один об'єкт — тоді буде `Row` з одним
елементом-об'єктом. `scalars()` знімає цю обгортку і віддає перший елемент
кожного рядка. Правило: **`select(Model)` → `scalars()`; `select(колонки)`
→ `execute()`.**

**Чому `get()` повертає `None`, а не кидає.** Відсутність запису — штатна
ситуація, а не помилка програми (згадай `dict.get` з уроку 3). Виняток —
`session.scalars(...).one()` і `.one_or_none()`, коли ти явно вимагаєш
«рівно один».

### Update

```python
book = session.get(Book, 1)
book.price = Decimal("275.00")
session.commit()
```

І все. Жодного `UPDATE` — сесія бачить зміну і генерує його сама, лише за
зміненими колонками. Це «прочитав → змінив → зберіг» — як `ПолучитьОбъект()`
→ змінити реквізит → `Записать()` у 1С.

Масове оновлення без читання об'єктів (Core-стиль, один `UPDATE`):

```python
from sqlalchemy import update

session.execute(
    update(Book).where(Book.stock == 0).values(price=Book.price * 0.9)
)
session.commit()
```

Об'єктів у пам'яті не буде, зате один запит замість тисячі.

### Delete

```python
orwell = session.scalar(select(Author).where(Author.name == "George Orwell"))
session.delete(orwell)
session.commit()
```

`delete()` — позначити; `DELETE` піде при `commit()`. Масове — `delete(Book)
.where(...)`, за аналогією з `update`.

Що з книгами Орвелла при видаленні автора? У `step_03` їх не було, тому
пройшло. Якби були — база кинула б `IntegrityError` через `FOREIGN KEY`,
бо в `Book.author` каскаду не оголошено. Це правильно: видалення автора
з книгами — рішення, яке має ухвалити людина, а не ORM.

### Помилка бази і `rollback()`

```python
book.stock = -10
try:
    session.commit()
except IntegrityError as error:
    session.rollback()
    print(error.orig.diag.message_primary)
# → new row for relation "books" violates check constraint "stock_not_negative"
```

Три речі:

1. `CheckConstraint` з моделі **спрацював у базі**, а не в Python.
   SQLAlchemy не перевіряє `stock >= 0` сама.
2. `IntegrityError` — обгортка SQLAlchemy; оригінальний виняток драйвера —
   в `error.orig`. У psycopg 3 з нього дістається `diag.message_primary` —
   чисте повідомлення без SQL.
3. **Після помилки сесію обов'язково `rollback()`.** Інакше вона
   «зламана»: будь-який наступний запит кине `PendingRollbackError`.
   Після відкату `session.get(Book, 1).stock` знову `4` — сесія перечитала
   з бази і забула наш `-10`.

---

## 6. Зв'язки: `relationship`

### 1:N у два боки

```python
class Author(Base):
    ...
    books: Mapped[list["Book"]] = relationship(back_populates="author")


class Book(Base):
    ...
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    author: Mapped["Author"] = relationship(back_populates="books")
```

Дві речі, які легко сплутати:

* **`author_id` + `ForeignKey`** — колонка. Вона є в таблиці, це просто
  число. Без неї зв'язку немає.
* **`author` + `relationship`** — атрибут **тільки в Python**. Колонки
  `author` у таблиці немає. Це і є «посилання» з 1С: `Книга.Автор.Наименование`
  замість `SELECT name FROM authors WHERE id = book.author_id`.

`back_populates` зв'язує два кінці: присвоїв `book.author = shevchenko` —
у `shevchenko.books` книга з'явилась сама, і навпаки. Імена в лапках
(`"Book"`) — бо клас `Book` оголошений нижче; SQLAlchemy розв'яже посилання
пізніше.

`Mapped[list["Book"]]` — «багато», `Mapped["Author"]` — «один». Анотація
знову працює: з неї SQLAlchemy розуміє, що з боку автора — колекція.

### Навігація

```python
author = session.scalar(select(Author).where(Author.name.like("%Orwell")))
[book.title for book in author.books]        # ['1984', 'Animal Farm']

order = session.get(Order, 1)
for item in order.items:
    item.book.title, item.book.price * item.quantity
```

Три рівні вглиб (`order → items → book`) без жодного `JOIN` у коді. Це
найзручніша риса ORM і одночасно джерело її головної проблеми.

### Lazy loading і проблема N+1

За замовчуванням `relationship` — **лінивий**: `author.books` не
завантажується разом з автором, а робить окремий `SELECT` у момент, коли
ти вперше до нього звернувся. Наслідок:

```python
for book in session.scalars(select(Book)):     # 1 запит
    print(book.author.name)                    # + по запиту на автора
```

Для 100 книг — до 101 запиту. Це **N+1** — найпоширеніша помилка
продуктивності з ORM, і саме тому досвідчені DBA ORM не люблять. З
`step_04` (лічильник запитів через логер `sqlalchemy.engine`):

```
Ліниво (lazy): книг 6, запитів у базу — 4
З selectinload: запитів у базу — 2
```

(4, а не 7 — identity map зекономила на повторних авторах, див. розділ 4;
у справжніх даних авторів стільки ж, скільки книг, і буде повне N+1.)

**Ліки — сказати заздалегідь, що тобі треба:**

```python
from sqlalchemy.orm import selectinload, joinedload

select(Book).options(selectinload(Book.author))   # 2 запити: книги + авторів IN (...)
select(Book).options(joinedload(Book.author))     # 1 запит із LEFT JOIN
```

* `selectinload` — другий запит `SELECT ... FROM authors WHERE id IN (1, 2,
  3)`. Універсальний вибір для колекцій (`Author.books`).
* `joinedload` — один запит із `JOIN`. Добре для «один» (`Book.author`),
  для колекцій роздуває результат (кожна книга повторюється стільки разів,
  скільки в неї позицій).

Правило: **у циклі по об'єктах, де торкаєшся зв'язку, — завжди
`options(...)`.** Увімкни `echo=True` і подивись, скільки `SELECT` пішло —
це найдешевша перевірка.

### Каскад

```python
class Order(Base):
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
```

`cascade` каже сесії, що робити зі зв'язаними об'єктами:

* `save-update` (є за замовчуванням) — `add(order)` додає і його `items`;
  саме він дав «ловушку порядку id» у розділі 5.
* `delete` — видалив замовлення → видалились позиції.
* `delete-orphan` — прибрав позицію зі списку `order.items` → вона
  видалиться з бази (стала «сиротою»).
* `all` = `save-update, merge, refresh-expire, expunge, delete`.

`step_04`: «Видалили замовлення; позицій залишилось: 0». Без каскаду це
впало б на `FOREIGN KEY`.

Це каскад **сесії**, у Python. Є ще каскад **бази** —
`ForeignKey("orders.id", ondelete="CASCADE")` — він працює навіть якщо
хтось видалить рядок через pgAdmin. Для «шапка — таблична частина» варто
мати обидва; для `Book.author` — жодного (розділ 5).

### Агрегати і JOIN через `select()`

```python
statement = (
    select(Author.name, func.count(Book.id), func.sum(Book.stock))
    .join(Author.books)
    .group_by(Author.name)
    .order_by(func.count(Book.id).desc())
)
for name, count, stock in session.execute(statement):
    ...
```

Той самий `GROUP BY` з уроку 8, тільки `func.count` замість `COUNT`, а
`.join(Author.books)` — `JOIN books ON books.author_id = authors.id`;
умову `ON` SQLAlchemy взяла з `relationship`. Результат — `Row`, який
розпаковується як кортеж.

### M:N — коротко

Для «книга — жанри» (з уроку 8) потрібна таблиця-зв'язка. У SQLAlchemy:

```python
book_genres = Table(
    "book_genres", Base.metadata,
    Column("book_id", ForeignKey("books.id"), primary_key=True),
    Column("genre_id", ForeignKey("genres.id"), primary_key=True),
)


class Book(Base):
    genres: Mapped[list["Genre"]] = relationship(
        secondary=book_genres, back_populates="books"
    )
```

`secondary=` — «через оцю таблицю». Далі `book.genres.append(genre)`, і
рядок у `book_genres` з'явиться сам. Якщо в таблиці-зв'язці є свої
колонки (дата, кількість — як у `OrderItem`), робиться повноцінна модель,
як у нас.

---

## 7. FastAPI + SQLAlchemy

### Три шари, які не змішуємо

```
HTTP-клієнт
    │  JSON
    ▼
Pydantic-схеми   BookIn / BookPatch / BookOut     ← контракт назовні
    │
    ▼
обробники        list_books, create_book, ...     ← склейка
    │
    ▼
моделі ORM       Book, Author                     ← як лежить у базі
    │
    ▼
PostgreSQL
```

Спокуса — використати модель SQLAlchemy як схему Pydantic, «щоб не
дублювати». Не треба: у базі є `author_id`, а назовні хочемо вкладеного
`author`; у базі є пароль, назовні — ні; на вхід — без `id`, на вихід —
з `id`. Це та сама думка уроку 7 «різні моделі на вхід і вихід», лише
тепер до неї додався третій, найглибший шар.

### Сесія через `Depends` з `yield`

```python
def get_session() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@app.get("/books/{book_id}", response_model=BookOut)
def get_book(book_id: int, session: SessionDep) -> Book:
    ...
```

Ось відповідь на питання 9 з повторення — «навіщо залежності з `yield`».
Код до `yield` виконується перед обробником (відкрили сесію), після —
після відповіді (закрили). Одна сесія на запит, рівно за правилом із
розділу 4. `Annotated[Session, Depends(...)]` винесено в `SessionDep`, щоб
не повторювати в кожному обробнику.

### `from_attributes` — з об'єкта ORM у Pydantic

```python
class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    price: Decimal
    stock: int
    author: AuthorOut
```

Pydantic за замовчуванням чекає словник. `from_attributes=True` дозволяє
йому читати поля **атрибутами** — `book.title`, `book.author.name` — і
збирати `BookOut` прямо з `Book`. Вкладене `author: AuthorOut` —
розв'язується через `relationship`. Це і є «переклад з кортежа в модель
руками», якого ми позбулись.

Обробник повертає `Book` (об'єкт ORM), `response_model=BookOut` перекладає.
Анотація `-> Book` — для IDE, `response_model` — для FastAPI.

### Обробники

```python
@app.post("/books", response_model=BookOut, status_code=201)
def create_book(data: BookIn, session: SessionDep) -> Book:
    if session.get(Author, data.author_id) is None:
        raise HTTPException(422, "Такого автора немає")
    book = Book(**data.model_dump())
    session.add(book)
    session.commit()
    session.refresh(book)
    return book
```

* `Book(**data.model_dump())` — словник Pydantic розпаковується в
  конструктор моделі: імена полів у `BookIn` збігаються з колонками.
* Перевірка автора — руками, до `INSERT`. Можна було б ловити
  `IntegrityError` від `FOREIGN KEY`, але тоді довелось би розбирати текст
  помилки бази; явна перевірка чесніша й дає зрозумілий 422.
* **`session.refresh(book)` після `commit()`** — інакше при серіалізації
  `BookOut` сесія полізе за кожним застарілим атрибутом окремо (expire після
  коміту, розділ 4), і серед них — `author`, лінивий. Один `refresh`
  замість кількох `SELECT`.

```python
@app.patch("/books/{book_id}", response_model=BookOut)
def patch_book(book_id: int, data: BookPatch, session: SessionDep) -> Book:
    book = get_book_or_404(session, book_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(book, field, value)
    session.commit()
    session.refresh(book)
    return book
```

`exclude_unset=True` з уроку 7 + `setattr` = `PATCH` за чотири рядки:
міняємо тільки те, що клієнт прислав, а сесія генерує `UPDATE` тільки за
цими колонками. Два шари «часткового оновлення» склались один в один.

```python
@app.get("/books", response_model=list[BookOut])
def list_books(session: SessionDep, limit: int = 20) -> list[Book]:
    statement = (
        select(Book).options(selectinload(Book.author))
        .order_by(Book.id).limit(limit)
    )
    return list(session.scalars(statement))
```

`selectinload(Book.author)` тут **обов'язковий**: `BookOut.author` торкнеться
автора кожної книги, і без нього список із 20 книг — це до 21 запиту на
кожен HTTP-виклик.

### Перевірено

```
GET    /books?limit=2              200  [{'id': 1, 'title': 'Кобзар', ..., 'author': {'id': 1, 'name': 'Тарас Шевченко'}}, ...]
POST   /books  (валідні дані)      201  {'id': 7, 'title': 'Заповіт', ...}
POST   /books  (author_id=999)     422  {'detail': 'Такого автора немає'}
POST   /books  (title="", price=-1) 422  String should have at least 1 character
PATCH  /books/7  {"stock": 9}      200  {'id': 7, ..., 'stock': 9}
DELETE /books/7                    204
GET    /books/7                    404  {'detail': 'Книги немає'}
```

Порт — `8011`: `8000` на цій машині зайнятий стороннім сервісом.

---

## 8. Часті помилки

| Симптом | Причина | Ліки |
|---|---|---|
| `ArgumentError: Textual SQL expression ... should be explicitly declared as text()` | `execute("SELECT ...")` рядком | обгорнути в `text()` |
| Дані не збереглись, помилок нема | `engine.connect()` без `commit()` / сесія без `commit()` | `engine.begin()` або явний `commit()` |
| `PendingRollbackError` | після винятку не зробили `rollback()` | `try/except` → `session.rollback()` |
| `DetachedInstanceError` / `Parent instance is not bound to a Session` | звернулись до лінивого зв'язку після закриття сесії | завантажити через `options(selectinload(...))` до закриття, або працювати всередині `with` |
| `column ... does not exist` | додали поле в клас, а таблиця стара | `drop_all/create_all` на навчанні, Alembic у бою |
| Сотні `SELECT` в логу на один список | N+1 | `selectinload` / `joinedload` |
| `MissingGreenlet` | синхронний доступ до лінивого зв'язку в async-коді | тема наступного уроку; поки — sync + `selectinload` |
| `IntegrityError ... violates foreign key constraint` при видаленні | є залежні рядки, каскаду немає | `cascade="all, delete-orphan"` / `ondelete="CASCADE"` / вирішити руками |
| `id` після `add_all` не в тому порядку | каскад `save-update` обходить граф у глибину | окремі `add()` + `flush()` |
| `session.get(...)` повернув «старе» значення | identity map віддав об'єкт з пам'яті | `session.expire_all()` / `refresh(obj)` |
| Модель Pydantic не збирається з об'єкта ORM | забули `from_attributes=True` | додати в `model_config` |

---

## 9. Шпаргалка

```python
# Підключення
engine = create_engine("postgresql+psycopg://user:pass@host:5432/db", echo=False)
SessionLocal = sessionmaker(bind=engine)

# Модель
class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    note: Mapped[str | None]                         # NULL дозволено
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    author: Mapped["Author"] = relationship(back_populates="books")

Base.metadata.create_all(engine)

# CRUD
with SessionLocal() as session:
    session.add(Book(...));            session.commit()          # C
    session.get(Book, 1)                                          # R за ключем
    session.scalars(select(Book).where(Book.stock > 0)).all()    # R список
    session.scalar(select(Book).where(Book.title == "..."))      # R один/None
    session.execute(select(Book.title, func.count()).group_by(Book.title))
    book.price = 100;                  session.commit()          # U
    session.execute(update(Book).where(...).values(...))          # U масово
    session.delete(book);              session.commit()          # D
    session.execute(delete(Book).where(...))                      # D масово

# Зв'язки без N+1
select(Book).options(selectinload(Book.author))
select(Author).options(selectinload(Author.books))

# Помилка бази
try:
    session.commit()
except IntegrityError:
    session.rollback()

# FastAPI
def get_session():
    with SessionLocal() as session:
        yield session

class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
```

Порядок думок при написанні обробника: **знайти → перевірити → змінити →
commit → refresh → повернути.**

---

## 10. Переваги й недоліки ORM

### Переваги

* Клас замість `CREATE TABLE`, об'єкт замість кортежа — IDE підказує поля,
  перевірка типів ловить помилки до запуску.
* Один код під PostgreSQL, SQLite, MySQL — діалект у URL.
* Параметризація вбудована: ін'єкцію треба робити навмисно.
* Сесія сама рахує, що змінилось, і в якому порядку вставляти.
* Зв'язки — навігація крапкою, як у 1С.

### Недоліки

* **N+1** — ORM робить його непомітним, і це головна претензія DBA.
* Складні запити (віконні функції, CTE, `LATERAL`) через `select()`
  громіздкі — часом чесніше `text()`.
* Ще один шар для розуміння: коли щось не так, треба знати і SQL, і те,
  як ORM його генерує. `echo=True` — обов'язковий інструмент.
* Масові операції через об'єкти повільні — для мільйона рядків
  `update()`/`delete()` у Core-стилі або взагалі SQL.

### Підсумок одним рядком

ORM не звільняє від знання SQL — вона звільняє від його **написання**
у типових випадках, а знання уроку 8 потрібне, щоб бачити, що вона
написала за тебе.

---

## 11. Місток до уроку 10

Дві речі, які ми обійшли:

1. **Схема живе.** Сьогодні — `drop_all()` + `create_all()`. У бою так не
   можна: дані втрачаються. **Alembic** — міграції: кожна зміна класу
   → скрипт `ALTER TABLE`, який можна застосувати і відкотити. Це
   «Оновити конфігурацію БД» з 1С, тільки у вигляді файлів під git.

   **Alembic — «git для схеми»?** Схоже: міграція = коміт, ланцюжок ревізій
   з `down_revision`, `head`, `alembic history`, `upgrade`/`downgrade`,
   гілки й `merge`. Відрізняється: git зберігає **знімки** файлів, Alembic
   — **інструкції** переходу (`upgrade()` / `downgrade()`, і зворотну треба
   написати самому); відкат `DROP COLUMN` даних не поверне; структура існує
   у трьох копіях (класи, скрипти, жива база), а `--autogenerate` лише
   порівнює першу з третьою і пише чернетку другої. Самі файли
   `migrations/versions/*.py` лежать у git — Alembic не замінює git, а живе
   всередині нього: `git pull` → `alembic upgrade head`.

   ```bash
   pip install alembic
   alembic init migrations
   alembic revision --autogenerate -m "add year to books"
   alembic upgrade head        # ALTER TABLE books ADD COLUMN year
   alembic downgrade -1
   ```
2. **Сесія синхронна**, а FastAPI — ASGI. Поки обробники `def` — усе
   гаразд (FastAPI гонить їх у пул потоків). Для `async def` потрібні
   `create_async_engine`, `AsyncSession` і драйвер `asyncpg`, а лінивий
   доступ до зв'язків там заборонений (`MissingGreenlet`) — `selectinload`
   стає обов'язковим.

---

## 12. Словник 1С → SQLAlchemy

| У 1С | У SQLAlchemy | Відмінність |
|---|---|---|
| Дерево конфігурації | `Base.metadata` | заповнюється успадкуванням від `Base`, не конфігуратором |
| Об'єкт метаданих (довідник) | клас-модель `class Book(Base)` | описується кодом |
| Реквізит | `Mapped[...] = mapped_column(...)` | тип і обов'язковість — з анотації |
| Реквізит типу `ДовідникПосилання.Автори` | `author_id: ForeignKey` **+** `author: relationship` | у 1С це один реквізит, тут — колонка і окремий Python-атрибут |
| `Книга.Автор.Наименование` | `book.author.name` | той самий вигляд; але кожне перше звертання — окремий `SELECT` (N+1) |
| `Автори.Книги` (підпорядкований довідник) | `author.books` через `back_populates` | |
| `СоздатьЭлемент()` | `Book(...)` | об'єкт ще не на «столі» — потрібен `session.add()` |
| `Записать()` | `session.commit()` | викликається на **сесії**, а не на об'єкті; записує все, що змінилось |
| `Ссылка.ПолучитьОбъект()` | `session.get(Book, id)` | повертає `None`, а не порожнє посилання |
| `Выбрать()` / запит | `session.scalars(select(Book).where(...))` | |
| `Удалить()` / позначка видалення | `session.delete(obj)` + `commit()` | позначки видалення немає — видаляється фізично |
| Таблична частина | окрема модель + `relationship(cascade="all, delete-orphan")` | каскад треба оголосити |
| Проведення документа (транзакція) | одна сесія: зміни → `commit()` / `rollback()` | |
| «Оновити конфігурацію БД» | `create_all()` (тільки нові таблиці) / Alembic (зміни) | `create_all` наявні таблиці не чіпає |
| Платформа перевіряє заповнення | база перевіряє `NOT NULL` / `CHECK` → `IntegrityError` | після винятку — обов'язково `rollback()` |

---

## 13. Проєкт за викладачем: `практика/bookshop`

Другу половину заняття робили проєкт крок у крок за викладачем. Домен —
не книги, а **користувачі та пости** (`User` 1:N `Post`). Чотири файли +
Alembic, база `shop_db` у тому ж Docker-контейнері `pg-lesson8`.

### Файли

| Файл | Що всередині |
|---|---|
| `database.py` | `DATABASE_URL`, `engine = create_engine(url, echo=True)`, `SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)`, `class Base(DeclarativeBase)` |
| `models.py` | `User(id, username unique, email unique, posts)`, `Post(id, title, content Optional, user_id FK, author)`, `cascade="all, delete-orphan"`, `__repr__` |
| `crud.py` | `create_user_with_posts`, `get_user_by_id`, `get_all_users`, `get_all_posts`, `update_user_email`, `delete_user` — **кожна сама відкриває сесію** |
| `main.py` | сценарій: 1 create → 2 get → 3 all posts → 4 update → 5 delete |
| `api.py` | те саме через FastAPI (бонус, не з уроку): `uvicorn api:app --port 8012` |
| `alembic/`, `alembic.ini` | міграція `595ee49cb2d9_create_users_and_posts` |

### Два параметри, які додав викладач

```python
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
```

* `echo=True` — кожен SQL у консоль. На занятті незамінно.
* `expire_on_commit=False` — після `commit()` об'єкти **не** позначаються
  застарілими. Інакше `print(user.id)` після коміту робить зайвий `SELECT`,
  а у FastAPI після закриття сесії — `DetachedInstanceError`. Ціна:
  об'єкт не дізнається про чужі зміни до `refresh()`. Для короткої сесії
  «на одну операцію» — прийнятно. Мій `bookshop` з розділу 7 обходив те
  саме через `session.refresh(obj)` після кожного `commit()`.

### Стиль CRUD: сесія всередині функції

```python
def create_user_with_posts(username: str, email: str, post_titles: list[str]):
    with SessionLocal() as session:
        try:
            user = User(username=username, email=email)
            for title in post_titles:
                user.posts.append(Post(title=title, content=f"Зміст для {title}"))
            session.add(user)          # один add — пости їдуть каскадом
            session.commit()           # одна транзакція: користувач + пости
            print(f"Created new user with id: {user.id}")
            return user
        except Exception as ex:
            session.rollback()         # без цього сесія «зламана»
            print(f"Error: {ex}")
            return None
```

* `user.posts.append(Post(...))` — `user_id` підставиться сам після
  `INSERT` користувача (`relationship` + `back_populates`).
* Два стилі, які **не можна змішувати** в одному файлі: «сесія приходить
  параметром» (`def f(session: Session, ...)`, для FastAPI через
  `Depends`) і «функція відкриває сесію сама» (викладач). Змішав — отримав
  `NameError: db is not defined`.
* Функції викладача лише друкують. Щоб їх міг використати API або
  наступний крок сценарію, додано `return user` / `return None` /
  `return True|False`.
* `session.scalars(stmt)` — ітератор, прив'язаний до сесії. Повертати
  його назовні з `with` не можна — після закриття сесії він порожній.
  Повертати `.all()` (список).

### Alembic на справжній базі

```bash
cd "d:\PY\Урок 9\практика\bookshop"
alembic init alembic
# alembic.ini:      sqlalchemy.url = postgresql://postgres:secret@localhost:5432/shop_db
# alembic/env.py:   from models import Base ; target_metadata = Base.metadata
alembic revision --autogenerate -m "create users and posts"
alembic upgrade head
alembic current          # 595ee49cb2d9 (head)
```

Файл міграції: `revision`/`down_revision` (ланцюжок), `upgrade()` з
`op.create_table(...)` — та сама модель, переписана командами;
`downgrade()` з `op.drop_table(...)` у зворотному порядку (спочатку
`posts`, бо в неї FK). `relationship` у міграцію не потрапляє — це не
колонка. Комент `please adjust!` — файл читають перед `upgrade`.

**Коли Alembic зайвий:** поки даних не шкода — `Base.metadata.create_all(engine)`
на старті `main.py`, одна строка. Переходити на Alembic у момент, коли в
базі з'явилось те, що не можна втратити. У 1С те саме робить «Оновити
конфігурацію БД» — той самий механізм (порівняти структури → `ALTER`),
просто схований.

### Ловушки, на які наступили сьогодні

| Симптом | Причина | Ліки |
|---|---|---|
| `No module named 'psycopg2'` | URL `postgresql://` без `+драйвер` = psycopg2 за замовчуванням; стояв лише psycopg 3 | `pip install psycopg2-binary` або `postgresql+psycopg://` |
| `alembic: не розпізнано як команда` | термінал без активованого venv і/або не та папка | `.\.venv-1\Scripts\Activate.ps1`, `cd` у папку з `alembic.ini` |
| Pylance: `Import "sqlalchemy.orm" could not be resolved` | аналізатор дивиться в системний Python, а не в `.venv-1` | `.vscode/settings.json` → `python.defaultInterpreterPath` на `.venv-1`; або `Python: Select Interpreter` |
| pgAdmin не бачить `shop_db` / нові таблиці | дерево кешується при розкритті | правий клік → **Refresh** на `Databases` / `Tables` |
| `relation "alembic_version" does not exist` у pgAdmin | Query Tool відкритий на іншій базі (`shop_orm`) | перемкнути базу у випадаючому списку зверху |
| `with SessionLocal as session:` | без дужок — це фабрика, а не сесія | `SessionLocal()` |
| `IndentationError` на `class Post` | зайвий пробіл перед `class` | прибрати |
| `Mapper 'Post' has no property 'author'` | `back_populates="author"` вказує на атрибут, якого немає | додати `author: Mapped["User"] = relationship(back_populates="posts")` |
| `AttributeError: 'NoneType' has no attribute 'id'` на 2-му запуску `main.py` | `admin` уже є → `UniqueViolation` → функція повернула `None` | перевірка `if user is None: raise SystemExit(1)`; або видалити `admin` у pgAdmin |
| `id` = 1, 4, 5, 7, 9… | `SERIAL` не повертає номери після відкату — послідовність живе поза транзакцією | норма; на суцільність `id` не покладатись |
| `DELETE FROM users` у pgAdmin → `violates foreign key constraint` | `cascade` у `relationship` — правило **сесії**, не бази | або видаляти через `crud.delete_user()`, або `ForeignKey(..., ondelete="CASCADE")` |

### Дрібниці, які запитували

* **`users`, а не `user`** — клас в однині, таблиця в множині; і `user` —
  зарезервоване слово PostgreSQL (`SELECT user` = поточний користувач БД).
* **`!r` у f-рядку** — `{x!r}` викликає `repr(x)`: рядок у лапках, `None`
  як `None`. У `__repr__` — завжди `!r`, щоб `title=''` не плутати з
  `title=None`.
* **psycopg** — драйвер (DB-API), нижній поверх; SQLAlchemy без нього
  нікуди не підключиться. `psycopg2` (2006) і `psycopg` v3 (2021) — різні
  пакети, `-binary`/`[binary]` — зібрані, без компілятора.
* **Групи команд SQL:** DDL (`CREATE/ALTER/DROP/TRUNCATE`) — у нас його
  пише `create_all`/Alembic; DML (`INSERT/UPDATE/DELETE`) — сесія; DQL
  (`SELECT`) — `session.get`/`select()`; TCL — `commit`/`rollback`; DCL
  (`GRANT`) — ORM не покриває.
* **ACID** — див. розділ 4.
