# Домашнє завдання

**Завдання 1:** створити віртуальне оточення (на свій вибір) і встановити пакети Django та
Flask. Результат — скріншоти: активоване віртуальне оточення та вивід команди `pip freeze`.

**Завдання 2:** написати 2–3 bash-файли, які працюють із вводом користувача.
Готові скрипти та їх опис — у папці [bash/](bash/README.md): `hello.sh`, `new_project.sh`,
`calc.sh`. Усі три перевірені запуском у Git Bash.

## Що вже зроблено

У цій папці вже створено оточення `venv` з Python 3.12.9, у ньому встановлені Django 6.1
і Flask 3.1.3, а список залежностей збережено у `requirements.txt`.

## Кроки — повтори їх сам, щоб зробити скріншоти

Відкрий термінал у папці `Урок 1\homework`.

```powershell
# 1. створити оточення (якщо робиш з нуля — спочатку видали папку venv)
python -m venv venv

# 2. активувати  ←  СКРІНШОТ 1: у рядку з'явився префікс (venv)
.\venv\Scripts\activate

# 3. перевірити, що працює саме оточення
python --version
where.exe python        # перший рядок має вести у venv\Scripts

# 4. встановити пакети
pip install django flask

# 5. переконатися, що все на місці
python -c "import django, flask; print(django.get_version())"

# 6. подивитися список  ←  СКРІНШОТ 2: вивід pip freeze
pip freeze

# 7. зберегти список у файл (для здачі роботи)
pip freeze > requirements.txt

# 8. вийти з оточення
deactivate
```

> Якщо PowerShell лається «виконання сценаріїв вимкнено», один раз виконай:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

## Що має бути на скріншотах

1. **Активоване оточення** — видно рядок з префіксом `(venv)` і вивід `python --version`.
2. **Результат `pip freeze`** — у списку є `Django==6.1` і `Flask==3.1.3`
   (номери версій можуть відрізнятися — це нормально).

## Поточний результат `pip freeze`

asgiref==3.12.1
blinker==1.9.0
click==8.4.2
colorama==0.4.6
Django==6.1
Flask==3.1.3
itsdangerous==2.2.0
Jinja2==3.1.6
MarkupSafe==3.0.3
sqlparse==0.6.0
tzdata==2026.3
Werkzeug==3.1.8

Ти просив тільки Django і Flask, а в списку 12 рядків. Це нормально: `pip` разом із пакетом
ставить його **залежності** — те, без чого пакет не працює. Наприклад, Flask не вміє сам
малювати HTML-сторінки, тому тягне за собою `Jinja2`, а Django для роботи з базою тягне
`sqlparse`.

## Варіант через Poetry (якщо захочеш спробувати)

```bash
poetry init -n
poetry add django flask
poetry run python -c "import django; print(django.get_version())"
```

Poetry сам створить `.venv` і запише залежності у `pyproject.toml`.
