"""Приведення типів: int(), float(), str(), bool() і чому це головна тема уроку.

input() ЗАВЖДИ повертає рядок. Якщо забути перетворити його на число —
отримаєте або TypeError, або тихо неправильний результат.
"""

# --- 1. Явне перетворення ---

print(int("42"))        # 42     рядок -> ціле
print(int(3.9))         # 3      float -> int: дробова частина ВІДКИДАЄТЬСЯ, не округлюється
print(int(-3.9))        # -3
print(float("3.5"))     # 3.5
print(float(7))         # 7.0
print(str(42))          # '42'   число -> рядок
print(str(3.5))         # '3.5'


# --- 2. Що перетворити не вийде ---

# print(int("3.5"))     # ValueError: рядок з точкою int() не приймає
print(int(float("3.5")))   # 3 — спочатку у float, потім у int
# print(int("сорок"))   # ValueError: invalid literal for int() with base 10
# print(int(""))        # ValueError: порожній рядок


# --- 3. Класична помилка новачка ---

user_input = "5"             # уявіть, що це прийшло з input()
print(user_input + "5")      # '55'  — склеїлися РЯДКИ, а не додалися числа
print(int(user_input) + 5)   # 10    — ось так правильно
print(user_input * 3)        # '555' — рядок повторився тричі
print(int(user_input) * 3)   # 15


# --- 4. bool(): що Python вважає «правдою» ---

# Фальшиві (falsy) значення — їх варто просто запам'ятати:
print(bool(0))          # False
print(bool(0.0))        # False
print(bool(""))         # False — порожній рядок
print(bool([]))         # False — порожній список
print(bool({}))         # False — порожній словник
print(bool(()))         # False — порожній кортеж
print(bool(None))       # False

# Усе інше — True:
print(bool(1))          # True
print(bool(-5))         # True  (!) від'ємні числа теж True
print(bool("0"))        # True  (!) рядок "0" не порожній, отже True
print(bool("False"))    # True  (!) це просто непорожній рядок
print(bool(" "))        # True  (!) пробіл — це символ
print(bool([0]))        # True  — список з одного елемента непорожній

# Тому пишемо коротко:
items = []
if not items:
    print("список порожній")


# --- 5. bool — це підтип int ---

print(True + True)      # 2  (!) True == 1, False == 0
print(sum([True, False, True]))   # 2 — так рахують кількість «так» у списку
print(int(True), int(False))      # 1 0


# --- 6. Перевірка типу перед перетворенням ---

value = "123"

if value.isdigit():
    number = int(value)
    print(f"число: {number}")
else:
    print("це не число")

# Надійніший спосіб — спробувати і перехопити помилку (навчимо детальніше далі):
raw = "не число"
try:
    print(int(raw))
except ValueError:
    print(f"«{raw}» не перетворюється на число")


# --- 7. isinstance() — правильна перевірка типу ---

age = 30
print(isinstance(age, int))          # True
print(isinstance(age, str))          # False
print(isinstance(age, (int, float)))  # True — «або int, або float»
print(type(age) is int)              # True — теж працює, але isinstance гнучкіший
