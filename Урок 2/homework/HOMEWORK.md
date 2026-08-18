# Домашнє завдання — Урок 2 (Git)

Тема: локальний репозиторій, коміти, гілки, GitHub / GitLab, PR, конфлікти.

## Завдання 1. Налаштування (скріншот)

```bash
git --version
git config --list
```

Здаємо скріншот, де видно версію Git та ваші `user.name` / `user.email`.

## Завдання 2. Локальний репозиторій і 5 комітів

1. Створи папку `hw2_git`, зроби `git init`.
2. Додай файл `main.py` з будь-якою програмою з Уроку 1.
3. Зроби **щонайменше 5 комітів**, кожен — одна логічна зміна
   (наприклад: `add main.py`, `add greeting function`, `add docstring`,
   `fix typo`, `add gitignore`).
4. Додай `.gitignore` з `.venv/`, `__pycache__/`, `*.pyc`, `.env`.
5. Покажи історію:

```bash
git log --oneline --graph --all
```

Здаємо скріншот історії.

## Завдання 3. GitHub

1. Створи акаунт на GitHub (якщо ще немає).
2. Згенеруй SSH-ключ і додай його в **Settings → SSH and GPG keys**.
3. Перевір: `ssh -T git@github.com`.
4. Створи репозиторій `hw2_git` і запуш свій проєкт:

```bash
git remote add origin git@github.com:USERNAME/hw2_git.git
git push -u origin main
```

Здаємо посилання на репозиторій.

## Завдання 4. Гілка + Pull Request

1. Створи гілку `feature/calc`:

```bash
git checkout -b feature/calc
```

2. Додай у проєкт файл `calc.py` з двома функціями (`add`, `sub`) і закомітьте.
3. Запуш гілку: `git push origin feature/calc`.
4. На GitHub створи **Pull Request** з описом змін.
5. Зілий PR кнопкою **Merge** (тип — `Merge commit`).
6. Локально забери зміни: `git pull origin main`.
7. Видали гілку локально й на сервері:

```bash
git branch -d feature/calc
git push origin -d feature/calc
```

Здаємо скріншот PR (можна вже змерджений).

## Завдання 5. Конфлікт своїми руками

Зроби конфлікт спеціально (як у `practice/PRACTICE.md`, крок 8), виріши його
і закомітьте з повідомленням `resolve conflict`.

Здаємо скріншот файлу з маркерами `<<<<<<< ======= >>>>>>>` **до** вирішення
і `git log --oneline` **після**.

## Завдання 6. GitLab (додатково)

Створи проєкт на GitLab, додай туди той самий SSH-ключ і запуш другу копію
проєкту як другий remote:

```bash
git remote add gitlab git@gitlab.com:USERNAME/hw2_git.git
git push gitlab main
```

## Питання на самоперевірку

1. Чим Git відрізняється від GitHub?
2. Назви три зони Git і команду, яка переносить зміни між кожною парою.
3. Що зберігається в теці `.git` і що станеться, якщо її видалити?
4. Навіщо потрібен `git add`, якщо можна було б комітити все одразу?
5. Чим `git fetch` відрізняється від `git pull`?
6. Що таке Pull Request і чим він відрізняється від `git merge`?
7. Чому паролі не можна комітити навіть один раз?
8. Що робить `git stash` і чим він відрізняється від коміту?

## Що здаємо

* посилання на репозиторій `hw2_git` на GitHub;
* скріншоти: `git config --list`, історія комітів, PR, вирішений конфлікт;
* відповіді на питання самоперевірки (текстом або файлом `ANSWERS.md`).
