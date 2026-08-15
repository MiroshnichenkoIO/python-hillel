"""Тести для calc.py. Запуск із папки уроку: pytest"""

from calc import add, sub


def test_add():
    assert add(2, 3) == 5


def test_add_negative():
    assert add(-2, 3) == 1


def test_add_zero():
    assert add(0, 0) == 0


def test_sub():
    assert sub(5, 3) == 2
