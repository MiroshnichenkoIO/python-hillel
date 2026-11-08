# ДЗ 25.1. Practical AI for Python Developers

**Книжковий магазин** на Django: каталог, кошик, замовлення з оплатою через
Stripe, ролі покупця й менеджера, дві мови інтерфейсу та асинхронне JSON API.
У цьому ДЗ проєкт покращено за допомогою AI: code review, тести моделей,
документація.

| Що здати | Де |
| --- | --- |
| Оновлений код | ця папка |
| Code review з AI | [AI_REVIEW.md](AI_REVIEW.md) |
| Список промптів | [AI_PROMPTS.md](AI_PROMPTS.md) |
| Coverage report | [coverage_report.txt](coverage_report.txt) — моделі **100 %**, увесь код **91 %** |

---

## Можливості

- **Каталог** — пошук за назвою, пагінація, сторінка книги.
- **Кошик у сесії** — додати, змінити кількість (не більше залишку), очистити.
- **Замовлення** — одна транзакція: створення замовлення, блокування книг
  (`select_for_update`) і списання залишків; якщо чогось бракує — відкат.
- **Оплата Stripe Checkout** + webhook, що позначає замовлення оплаченим.
  Сторінки оплати бачить лише власник замовлення.
- **Користувачі** — реєстрація (група «Покупці»), вхід, права менеджера на
  додавання / зміну / видалення книг.
- **Українська та англійська** — моделі, форми, шаблони, повідомлення;
  перемикач мови в шапці.
- **Async API** — 4 асинхронні в'юхи з async ORM (`aget`, `acount`,
  `aaggregate`, `async for`, `request.auser()`).
- Лог запитів (middleware), Debug Toolbar, Docker Compose з PostgreSQL і Redis.

## Стек

Python 3.12 · Django 6.1 · PostgreSQL 16 / SQLite · Redis 7 · Stripe ·
pytest + pytest-django + factory-boy + pytest-cov · Docker Compose ·
gunicorn + whitenoise

## Структура

```text
homework/
├── bookshop/          налаштування, кореневі URL, ASGI/WSGI
├── shop/              книги й категорії, async API, middleware, seed_shop
│   └── tests/         pytest: фабрики, моделі, i18n, async views
├── cart/              кошик у сесії
├── orders/            замовлення, Stripe, webhook, лист покупцю
├── users/             CustomUser, реєстрація
├── templates/         base.html, вхід і реєстрація
├── locale/            переклади en / uk (.po + .mo)
├── AI_REVIEW.md       code review з AI
├── AI_PROMPTS.md      промпти
└── coverage_report.txt
```

## Запуск локально

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt -r requirements.dev.txt
python manage.py migrate
python manage.py seed_shop        # категорії, книги, користувачі
python manage.py runserver
```

Відкрити <http://127.0.0.1:8000/>. Без змінної `POSTGRES_DB` проєкт працює
на SQLite.

## Запуск у Docker

```powershell
copy .env.example .env            # заповнити паролі та ключі Stripe
docker compose up --build
```

Сайт — <http://localhost:8019/>. Міграції виконує `docker-entrypoint.sh`.

## Тести й покриття

```powershell
pytest                                                   # 58 тестів
pytest --cov=shop --cov=orders --cov=cart --cov=users --cov-report=term-missing
```

| Модуль | Покриття |
| --- | --- |
| `shop/models.py` | 100 % |
| `orders/models.py` | 100 % |
| `users/models.py` | 100 % |
| увесь код (без міграцій і тестів) | 91 % |

Тести моделей, згенеровані з AI, — `shop/tests/test_models.py` і
`orders/test_models.py`; у кожному є коментар
`# Generated with AI, reviewed and modified`.

## API

| Метод | URL | Що повертає |
| --- | --- | --- |
| GET | `/api/books/?q=` | список книг з пошуком |
| GET | `/api/books/<id>/` | одна книга або 404 |
| GET | `/api/stats/` | кількість книг, середня ціна, залишок, книги за категоріями |
| GET | `/orders/api/my/` | замовлення поточного користувача (гість — 401) |

Мова відповіді — із заголовка `Accept-Language` або з перемикача на сайті.

## Переклади

Вихідні рядки — українською, переклад — англійською
(`locale/en/LC_MESSAGES/django.po`). Після зміни текстів:

```powershell
python manage.py makemessages -l en -l uk
python manage.py compilemessages -l en -l uk
```

На Windows потрібен GNU gettext: `winget install mlocati.GetText`.

---

## AI Usage

**Інструмент:** Claude (Anthropic) у Claude Code — модель працювала з
файлами проєкту напряму, запускала тести й покриття.

| Задача | Що зробив AI | Що зроблено вручну / перевірено |
| --- | --- | --- |
| Code review | 3 в'юхи `orders`: знайшов IDOR на сторінках оплати, ризик deadlock, `ValueError` як прапорець, `KeyError` у webhook, N+1 | 3 поради з 14 відхилено як невалідні або зайві; кожну прийняту закрито тестом |
| Тести | 20 тестів для `Category`, `Book`, `Order`, `OrderItem` | перевірено `Decimal`, стабільність `ordering`; один тест переписано після падіння |
| Docstrings | одне речення для кожної в'юхи (`shop`, `cart`, `orders`, `users`) | звірено з тим, що в'юха робить насправді |
| README | структура, команди, таблиці | команди звірено з файлами проєкту |

**Промпти** (повний текст — у [AI_PROMPTS.md](AI_PROMPTS.md)):

1. *Вибір в'юх:* «Ти — senior Django-розробник… назви 3 найскладніші views
   для code review…»
2. *Рев'ю:* «Зроби code review функції … Шукай: помилки з 500, безпеку,
   транзакції, N+1. Не переписуй під себе. Формат: таблиця…»
3. *Самоперевірка:* «Перевір свої рекомендації: реальна проблема чи загальна
   порада? Чи потрібен @csrf_exempt на вебхуку?»
4. *Застосування:* «Застосуй прийняті рекомендації… запусти тести…»
5. *Тести:* «Ти — QA-інженер… pytest-тести для Category, Book, Order,
   OrderItem… фабрики factory-boy… коментар у кожному тесті»
6. *Покриття:* «Запусти pytest --cov… мета ≥ 60 %…»
7. *Docstrings:* «…одне речення українською, що робить в'юха з погляду
   користувача…»
8. *README:* «Читач — викладач… тільки команди, що реально є в проєкті…»

**Висновок.** AI добре знаходить типові проблеми (доступ до чужих даних,
N+1, необроблені ключі) і швидко пише шаблонні тести. Але частина порад —
загальні і в цьому проєкті хибні (прибрати `@csrf_exempt` з вебхука Stripe),
тому кожна рекомендація перевірялась тестом, а не приймалась на віру.
