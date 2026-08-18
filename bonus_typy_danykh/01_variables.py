"""Змінні та типи даних — з чого складається будь-яка програма.

Змінна — це ім'я, яке вказує на значення в пам'яті.
Python сам визначає тип за значенням (динамічна типізація),
але тип у значення завжди є, і його можна подивитися через type().
"""

from decimal import Decimal

# --- 1. Створення змінної: ім'я = значення ---

name = "Ігор"        # str   — рядок
age = 30             # int   — ціле число
height = 1.82        # float — число з дробовою частиною
is_student = True    # bool  — True / False
nothing = None       # NoneType — «значення відсутнє»

print(name, age, height, is_student, nothing)

# type() показує тип значення
print(type(name))        # <class 'str'>
print(type(age))         # <class 'int'>
print(type(height))      # <class 'float'>
print(type(is_student))  # <class 'bool'>
print(type(nothing))     # <class 'NoneType'>


# --- 2. Імена змінних: правила і стиль (PEP 8) ---

# Можна: літери, цифри, підкреслення. Починати з цифри — не можна.
user_count = 10          # правильно: snake_case, зрозуміла назва
# userCount = 10         # так пишуть у JavaScript, у Python — ні
# 2user = 10             # SyntaxError: ім'я не може починатися з цифри
# list = [1, 2]          # так можна, але НЕ треба: затираємо вбудовану назву
print(user_count)

# Константи пишемо ВЕЛИКИМИ літерами (Python не забороняє їх змінювати —
# це домовленість між програмістами «не чіпай це значення»).
MAX_ATTEMPTS = 3
PI = 3.14159
print(MAX_ATTEMPTS, PI)


# --- 3. Змінна — це ярлик, а не коробка ---

a = [1, 2, 3]
b = a            # b вказує на ТОЙ САМИЙ список, копії не було
b.append(4)
print(a)         # [1, 2, 3, 4] — змінився і a, бо це один об'єкт

c = a.copy()     # ось так робимо справжню копію
c.append(5)
print(a)         # [1, 2, 3, 4] — a не постраждав
print(c)         # [1, 2, 3, 4, 5]

# Для чисел і рядків такої пастки немає: вони незмінні (immutable).
x = 5
y = x
y += 1
print(x, y)      # 5 6


# --- 4. Кілька присвоєнь одразу ---

first, second = 1, 2
print(first, second)           # 1 2

first, second = second, first  # обмін значеннями без третьої змінної
print(first, second)           # 2 1

zero_a = zero_b = 0            # обидві дорівнюють 0
print(zero_a, zero_b)


# --- 5. Незмінні та змінювані типи (важливо запам'ятати) ---

# Незмінні (immutable): int, float, bool, str, tuple, frozenset
# Змінювані (mutable):  list, dict, set

text = "кіт"
# text[0] = "р"    # TypeError: рядок змінити не можна
text = "рік"       # можна лише перепризначити змінну на новий рядок
print(text)

animals = ["кіт", "пес"]
animals[0] = "лис"  # список змінюється «на місці»
print(animals)      # ['лис', 'пес']


# --- 6. Дрібниця, яку варто знати одразу: float неточний ---

print(0.1 + 0.2)                        # 0.30000000000000004
print(Decimal("0.1") + Decimal("0.2"))  # 0.3 — для грошей беремо Decimal
