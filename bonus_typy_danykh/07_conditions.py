"""Умови: if / elif / else. Перше місце, де програма починає «думати»."""

# --- 1. Базова конструкція ---

age = 20

if age >= 18:
    print("Дорослий")          # цей рядок належить if — бо він з відступом
else:
    print("Неповнолітній")

# Відступ у Python — це синтаксис, а не краса. Стандарт PEP 8: 4 пробіли.
# Двокрапка в кінці рядка з if / elif / else — обов'язкова.


# --- 2. if без else ---

temperature = 30
if temperature > 25:
    print("Спекотно, беремо воду")
print("Ця строка виконається завжди — вона без відступу")


# --- 3. elif — перевірка кількох варіантів по черзі ---

score = 78

if score >= 90:
    grade = "відмінно"
elif score >= 75:
    grade = "добре"
elif score >= 60:
    grade = "задовільно"
else:
    grade = "незадовільно"

print(f"Оцінка: {grade}")

# Важливо: Python перевіряє умови ЗВЕРХУ ВНИЗ і виходить після першої True.
# Тому порядок умов має значення — якби «score >= 60» стояло першим,
# усі оцінки вище 60 отримали б «задовільно».


# --- 4. Вкладені умови ---

has_ticket = True
has_passport = True

if has_ticket:
    if has_passport:
        print("Проходьте на борт")
    else:
        print("Потрібен паспорт")
else:
    print("Потрібен квиток")

# Те саме коротше — через and (читається легше, вкладеність не потрібна):
if has_ticket and has_passport:
    print("Проходьте на борт")
elif not has_ticket:
    print("Потрібен квиток")
else:
    print("Потрібен паспорт")


# --- 5. Умова на «правдивість» об'єкта ---

items = []

if items:                       # непорожній список — True
    print(f"У списку {len(items)} елементів")
else:
    print("Список порожній")

# Так писати НЕ треба, хоч і працює:
# if len(items) > 0:
# if items != []:


# --- 6. Тернарний оператор — if в один рядок ---

age = 20
status = "дорослий" if age >= 18 else "дитина"
print(status)

# Використовуйте лише для коротких виразів. Довгу логіку — звичайним if.


# --- 7. match / case — заміна довгого elif (Python 3.10+) ---

command = "stop"

match command:
    case "start":
        print("Запуск")
    case "stop":
        print("Зупинка")
    case "pause" | "hold":       # «або»
        print("Пауза")
    case _:                      # _ — «усі інші варіанти», аналог else
        print(f"Невідома команда: {command}")


# --- 8. pass — заглушка, коли гілка ще не написана ---

if age > 100:
    pass          # «нічого не роби» — потрібно, бо порожній блок = SyntaxError
else:
    print("Вік у нормі")


# --- 9. Маленька повна програма ---

def check_password(password: str) -> str:
    """Перевірити пароль і повернути текст висновку."""
    if len(password) < 8:
        return "Занадто короткий: мінімум 8 символів"
    if password.isdigit():
        return "Пароль лише з цифр — ненадійно"
    if password.lower() == password:
        return "Додайте хоч одну велику літеру"
    return "Пароль підходить"


print(check_password("123"))
print(check_password("12345678"))
print(check_password("parolparol"))
print(check_password("ParolParol"))
