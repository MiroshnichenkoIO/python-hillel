"""Перевірка віртуального оточення.

Скрипт показує, яким інтерпретатором він запущений і чи перебуває цей
інтерпретатор усередині віртуального оточення. Запусти його двічі:
до активації оточення і після — та порівняй вивід.
"""

import sys
from pathlib import Path


def is_virtual_env() -> bool:
    """Повернути True, якщо скрипт запущено всередині віртуального оточення.

    У звичайного Python шляхи sys.prefix і sys.base_prefix збігаються.
    Усередині venv sys.prefix вказує на папку оточення, а sys.base_prefix —
    на «справжній» Python, від якого оточення створено.
    """
    return sys.prefix != sys.base_prefix


def main() -> None:
    print("Версія Python:      ", sys.version.split()[0])
    print("Файл інтерпретатора:", sys.executable)
    print("sys.prefix:         ", sys.prefix)
    print("sys.base_prefix:    ", sys.base_prefix)

    if is_virtual_env():
        print("\nОточення АКТИВНЕ. Папка оточення:", Path(sys.prefix).name)
    else:
        print("\nОточення НЕ активне — працює глобальний Python.")
        print("Активуй його командою: .\\venv\\Scripts\\activate")


if __name__ == "__main__":
    main()
