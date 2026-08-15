# Урок 1

## Конспекти (PDF)

| Файл | Що всередині |
| --- | --- |
| `Урок 1 - Віртуальне оточення.pdf` | навіщо оточення, venv, pip, requirements.txt, Poetry |
| `Урок 1 - Основи Bash.pdf` | команди термінала і перший bash-скрипт |
| `Урок 1 - Якість коду (flake8, black).pdf` | перевірка стилю та автоформатування |
| `Урок 1 - pytest (перші тести).pdf` | навіщо потрібні тести і як їх писати |
| `Урок 1 - Запуск .sh і компіляція в .exe.pdf` | три способи запустити .sh, помилки, PyInstaller |

## Файли для практики

| Файл | Навіщо |
| --- | --- |
| `check_env.py` | показує, чи активне віртуальне оточення |
| `backup.sh` | приклад bash-скрипта з уроку |
| `style_demo/bad.py` | код з помилками стилю — тренуємося на ньому |
| `style_demo/good.py` | той самий код за PEP 8, з поясненням кожної правки |
| `calc.py` + `test_calc.py` | програма і тести до неї для pytest |
| `requirements-example.txt` | приклад файлу зі списком залежностей |
| `homework/` | домашнє завдання: оточення з Django та Flask, bash-скрипти |
| `exe_demo/greet.py` | програма, з якої ми зробили `greet.exe` через PyInstaller |

## Головні думки уроку

1. **Оточення** — у кожного проєкту своя «коробка» з бібліотеками, версії не конфліктують.
2. **Термінал** — команди словами швидші за мишку, і їх можна записати у скрипт.
3. **Якість коду** — `black` наводить лад, `flake8` перевіряє, що лад є.
4. **Тести** — один раз написав перевірку, далі комп'ютер перевіряє код за тебе.

## Шпаргалка

```bash
# оточення
python -m venv venv              # створити
.\venv\Scripts\activate          # активувати (Windows)
source venv/bin/activate         # активувати (macOS / Linux)
pip install requests             # поставити бібліотеку
pip list                         # що встановлено
pip freeze > requirements.txt    # зберегти список
pip install -r requirements.txt  # відновити за списком
deactivate                       # вийти

# термінал
pwd                              # де я
ls                               # що навколо
cd folder_name                   # зайти в папку
mkdir test_folder                # створити папку
touch file.py                    # створити файл
cat file.py                      # показати вміст
rm file.py                       # видалити файл (без кошика!)

# якість коду і тести
black .                          # відформатувати
flake8 your_script.py            # перевірити стиль
pytest                           # запустити тести
```

## Практика: пройди по кроках

1. Запусти `python check_env.py` **без** оточення, потім активуй його і запусти ще раз —
   порівняй `sys.prefix` і `sys.base_prefix`.
2. Встанови інструменти: `pip install flake8 black pytest`.
3. Зайди в `style_demo`, виконай `flake8 bad.py` і прочитай зауваження. Потім `black bad.py`
   і порівняй результат із `good.py`.
4. У папці уроку виконай `pytest -v` — має бути 4 passed.
5. Зламай функцію `add` у `calc.py` (наприклад, `return a - b`), знову запусти `pytest`
   і подивись, як виглядає тест, що впав. Поверни як було.
6. Збережи залежності: `pip freeze > requirements.txt`.

## Домашнє завдання

Дивись [homework/HOMEWORK.md](homework/HOMEWORK.md) — оточення з Django та Flask
і два скріншоти для здачі.

## Додаткові матеріали

- [Віртуальні оточення (Real Python)](https://realpython.com/python-virtual-environments-a-primer/)
- [Що таке pip (Real Python)](https://realpython.com/what-is-pip/)
- [Документація pip](https://pip.pypa.io/en/stable/)
- [Каталог пакетів PyPI](https://pypi.org/)
- [Документація Poetry](https://python-poetry.org/docs/)
- [Bash Cheat Sheet](https://github.com/RehanSaeed/Bash-Cheat-Sheet)
- [PEP 8 — стиль коду](https://peps.python.org/pep-0008/)
- [Документація flake8](https://flake8.pycqa.org/en/latest/)
- [Документація black](https://black.readthedocs.io/en/stable/)
- [Документація pytest](https://docs.pytest.org/en/stable/)
