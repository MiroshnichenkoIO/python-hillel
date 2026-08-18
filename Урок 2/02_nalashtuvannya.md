# 2. Встановлення та перше налаштування

## Встановлення

Завантаж Git: <https://git-scm.com/downloads>

На Windows разом із Git встановлюється **Git Bash** — термінал з unix-командами
(`ls`, `pwd`, `touch`), той самий, який ми вчили в Уроці 1.

Перевірка:

```bash
git --version
# git version 2.51.0.windows.1
```

Якщо команда не знайдена — Git не додався в `PATH`: перевстанови з опцією
«Git from the command line and also from 3rd-party software» або перезапусти термінал.

## Налаштування (робиться один раз)

```bash
git config --global user.name "Твоє ім'я"
git config --global user.email "email@example.com"
git config --global init.defaultBranch main
```

Що це означає:

* `user.name` і `user.email` **вписуються в кожен коміт** як автор. Це не логін
  і не пароль — просто підпис. Ставте той email, що й на GitHub, інакше коміти
  не зв'яжуться з вашим профілем;
* `init.defaultBranch main` — нові репозиторії стартують з гілки `main`
  (історично було `master`, зараз стандарт — `main`);
* `--global` = для всіх ваших проєктів. Без цього прапорця налаштування
  діє лише для поточного репозиторію (буває потрібно для робочої пошти).

Корисні додатки до налаштувань:

```bash
git config --global core.autocrlf true     # Windows: правильні переноси рядків
git config --global core.editor "code --wait"   # редактор для commit-повідомлень
```

Перевірити налаштування:

```bash
git config --list                # усі налаштування
git config user.name             # одне конкретне
git config --list --show-origin  # плюс файл, з якого воно взялося
```

## Створення локального репозиторію

```bash
mkdir my_project
cd my_project
git init
```

Git створить приховану теку `.git`, де зберігатиме всі версії коду.

```bash
ls -a          # побачиш .git серед файлів
git status
```

Типовий вивід `git status` у порожньому репозиторії:

```
On branch main

No commits yet

nothing to commit (create/copy files and use "git add" to track)
```

Що варто знати про `.git`:

* уся історія проєкту лежить **усередині** цієї теки;
* видалиш `.git` — залишаться лише поточні файли, історія зникне назавжди;
* руками там нічого редагувати не потрібно;
* `.git` створюється один раз на проєкт. Робити `git init` усередині
  вже існуючого репозиторію — типова помилка новачка.

## `.gitignore` — що НЕ потрапляє в репозиторій

Не все треба зберігати в історії: віртуальне оточення, кеші, паролі,
файли IDE. Створюємо файл `.gitignore` у корені проєкту (приклад для Python
лежить у цій папці — `gitignore_example.txt`).

```gitignore
.venv/
venv/
__pycache__/
*.pyc
.env
.idea/
.vscode/
```

Головне правило: **паролі, ключі й токени в Git не потрапляють ніколи**.
Один раз закомітив — воно залишиться в історії навіть після видалення файлу.

## Перевірка, що все готове

```bash
git --version        # Git встановлено
git config user.name # підпис заданий
git status           # репозиторій існує
```
