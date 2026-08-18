"""Оператори: порівняння, логічні, in, is. Результат — завжди True або False."""

# --- 1. Порівняння ---

print(5 == 5)     # True   дорівнює (два знаки «=»!)
print(5 != 3)     # True   не дорівнює
print(5 > 3)      # True
print(5 < 3)      # False
print(5 >= 5)     # True
print(5 <= 4)     # False

# Один «=» — це присвоєння, а не порівняння. Часта помилка:
# if age = 18:    # SyntaxError
# if age == 18:   # правильно

# Рядки порівнюються за алфавітом (точніше — за кодами символів)
print("apple" < "banana")   # True
print("Apple" < "apple")    # True — великі літери мають менші коди
print("2" > "10")           # True (!) це РЯДКИ: порівнявся "2" з "1"
print(2 > 10)               # False — а це числа


# --- 2. Ланцюжок порівнянь — так можна лише в Python ---

age = 25
print(18 <= age <= 65)          # True — читається як у математиці
# В інших мовах треба було б: age >= 18 and age <= 65


# --- 3. Логічні оператори: and, or, not ---

print(True and True)     # True   — «і»: обидва мають бути True
print(True and False)    # False
print(True or False)     # True   — «або»: достатньо одного True
print(False or False)    # False
print(not True)          # False  — заперечення

has_ticket = True
has_passport = False
print(has_ticket and has_passport)        # False — потрібно і те, і те
print(not has_passport)                   # True


# --- 4. Ліниве обчислення (short-circuit) ---

# and: якщо ліва частина False — права навіть не обчислюється.
# or:  якщо ліва частина True  — права навіть не обчислюється.

items = []
# print(items[0] > 0)                     # IndexError
print(len(items) > 0 and items[0] > 0)    # False — до items[0] справа не дійшло

# Практичний приклад: спочатку перевіряємо, що дані є
name = ""
if name and name[0].isupper():
    print("ім'я з великої літери")
else:
    print("ім'я порожнє або з маленької")


# --- 5. and / or повертають ЗНАЧЕННЯ, а не тільки True/False ---

print(0 or "значення за замовчуванням")   # 'значення за замовчуванням'
print("Ігор" or "гість")                  # 'Ігор'
print("Ігор" and "гість")                 # 'гість'

user_name = ""
display = user_name or "Анонім"           # частий прийом: підстановка дефолту
print(display)                            # Анонім


# --- 6. Пріоритет: not -> and -> or ---

print(True or False and False)     # True  — спочатку and, потім or
print((True or False) and False)   # False — дужки змінюють порядок
# Порада: не економте на дужках, коли вираз довший за два оператори.


# --- 7. in / not in — перевірка входження ---

print("мир" in "Привіт, мир")        # True  — підрядок у рядку
print(3 in [1, 2, 3])                # True  — елемент у списку
print("ко" in ["кіт", "пес"])        # False — у списку шукається елемент ЦІЛКОМ
print(5 not in [1, 2, 3])            # True

command = "quit"
if command in ("стоп", "вихід", "quit"):   # замість довгого ланцюжка or
    print("завершуємо роботу")


# --- 8. is проти == (класичне питання на співбесіді) ---

# ==  порівнює ЗНАЧЕННЯ
# is  порівнює, чи це ОДИН І ТОЙ САМИЙ об'єкт у пам'яті

a = [1, 2, 3]
b = [1, 2, 3]
c = a

print(a == b)    # True  — значення однакові
print(a is b)    # False — але це два різних списки
print(a is c)    # True  — одне й те саме
print(id(a) == id(c))   # True — id() показує адресу об'єкта

# is використовуємо практично лише з None:
value = None
print(value is None)      # True — так правильно
print(value is not None)  # False
# if value == None:       # працює, але так не пишуть
