"""Рядки (str): створення, зрізи, методи, f-рядки."""

# --- 1. Лапки: одинарні, подвійні, потрійні ---

single = 'текст'
double = "текст"          # для Python це одне й те саме
apostrophe = "О'Генрі"    # усередині подвійних вільно живе апостроф
quote = 'він сказав "так"'
multiline = """перший рядок
другий рядок"""           # потрійні лапки зберігають переноси

print(single, double, apostrophe, quote, sep=" | ")
print(multiline)


# --- 2. Спеціальні символи ---

print("рядок1\nрядок2")      # \n — перенос рядка
print("ім'я\tпрізвище")      # \t — табуляція
print("шлях: C:\\PY")        # \\ — сам знак backslash
print(r"шлях: C:\PY")        # r"" — «сирий» рядок, \ не має спецзначення


# --- 3. Довжина та доступ по індексу ---

word = "Python"
print(len(word))     # 6
print(word[0])       # P — індексація з нуля
print(word[5])       # n
print(word[-1])      # n — від'ємний індекс рахує з кінця
print(word[-2])      # o
# print(word[6])     # IndexError: string index out of range


# --- 4. Зрізи: word[початок:кінець:крок] ---

# Правило: початок включається, кінець — НІ.
print(word[0:2])     # Py
print(word[:2])      # Py    — від початку
print(word[2:])      # thon  — до кінця
print(word[:])       # Python — копія всього
print(word[::2])     # Pto   — кожен другий символ
print(word[::-1])    # nohtyP — рядок навпаки


# --- 5. Конкатенація та повторення ---

first_name = "Ігор"
last_name = "Мірошниченко"
print(first_name + " " + last_name)   # склеювання
print("-" * 20)                       # повторення: --------------------
# print("вік: " + 30)   # TypeError: рядок і число просто так не склеюються
print("вік: " + str(30))              # так — правильно


# --- 6. f-рядки — головний спосіб підставляти значення ---

age = 30
height = 1.8234

print(f"{first_name} {last_name}, {age} років")
print(f"наступного року буде {age + 1}")        # усередині {} можна вирази
print(f"зріст: {height:.2f} м")                 # .2f — два знаки після коми
print(f"{age:>10}|")                            # вирівнювання праворуч у 10 знаків
print(f"{first_name=}")                         # зручно для відладки: first_name='Ігор'

# Старіші способи (зустрінете в чужому коді):
print("{} {}".format(first_name, age))
print("%s %d" % (first_name, age))


# --- 7. Методи рядків (вони НЕ змінюють рядок, а повертають новий) ---

text = "  Привіт, Світ!  "

print(text.strip())            # 'Привіт, Світ!' — прибрати пробіли з країв
print(text.strip().lower())    # 'привіт, світ!'
print(text.strip().upper())    # 'ПРИВІТ, СВІТ!'
print(text.strip().title())    # 'Привіт, Світ!'
print(text.replace("Світ", "Python").strip())
print(text.strip().split(", "))    # ['Привіт', 'Світ!'] — розбити на список
print("-".join(["a", "b", "c"]))   # 'a-b-c' — зібрати список у рядок

print(text)   # рядок як був — з пробілами. str незмінний!

# Перевірки — повертають True / False
print("Привіт".startswith("При"))   # True
print("file.txt".endswith(".txt"))  # True
print("123".isdigit())              # True  — лише цифри
print("abc".isalpha())              # True  — лише літери
print("Світ" in text)               # True  — пошук підрядка
print(text.strip().find("Світ"))    # 8 — індекс входження (-1, якщо немає)
print(text.count("і"))              # скільки разів зустрічається символ
