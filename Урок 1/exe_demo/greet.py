"""Маленька програма для демонстрації: як із .py зробити .exe.

Вона питає ім'я і вік — так само, як bash-скрипт hello.sh, тільки мовою Python.
"""

import os
import sys
from datetime import date


def setup_console() -> None:
    """Навчити консоль Windows показувати українські літери.

    Стара консоль Windows за замовчуванням працює в кодуванні cp866, і замість
    «Привіт» виходять «кракозябри». chcp 65001 перемикає її на UTF-8.
    """
    if sys.platform == "win32":
        os.system("chcp 65001 > nul")
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")


def main() -> None:
    setup_console()

    print("=== Знайомство (версія на Python) ===")

    name = input("Як тебе звати? ").strip() or "незнайомець"
    age_text = input("Скільки тобі років? ").strip()

    if not age_text.isdigit():
        print("Це не схоже на число. Наступного разу введи, наприклад, 12.")
    else:
        age = int(age_text)
        born = date.today().year - age
        print(f"\nПривіт, {name}!")
        print(f"Тобі {age} років, отже ти народився приблизно у {born} році.")

    # Без цього рядка вікно .exe закриється миттєво і ти нічого не встигнеш прочитати
    input("\nНатисни Enter, щоб закрити вікно...")


if __name__ == "__main__":
    main()
