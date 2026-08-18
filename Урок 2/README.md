# Урок 2 — Git: система контролю версій

## Файли уроку

| Файл | Навіщо |
| --- | --- |
| `Урок 2 - Git простими словами.pdf` | **почни звідси**: уся теорія на простих аналогіях (9 сторінок) |
| `01_teoriya.md` | Git vs GitHub vs GitLab, три зони, історія, інтеграція в IDE |
| `02_nalashtuvannya.md` | встановлення, `git config`, `git init`, `.gitignore` |
| `03_robota_z_failamy.md` | `status`, `add`, `commit`, `log`, `diff`, `restore` — щоденний цикл |
| `04_github_ssh.md` | `remote`, `push`, SSH-ключі, типові помилки |
| `05_gitlab.md` | GitLab: проєкт, ключі, MR замість PR, два remote |
| `06_branches_pr_merge.md` | гілки, Pull Request, типи merge, `pull`/`fetch`, конфлікти, `stash` |
| `07_korysni_fishky.md` | `blame`, `revert`, `checkout <hash>`, `reflog`, alias, пошук по історії |
| `GIT_CHEATSHEET.md` | шпаргалка з усіма командами уроку на одній сторінці |
| `practice/PRACTICE.md` | покрокова практика в піщаниці — 11 кроків з власним репозиторієм |
| `homework/HOMEWORK.md` | домашнє завдання |

Джерело PDF — `Урок 2 - Git простими словами.html`. Якщо правиш текст, зміни html
і перезбери PDF (у браузері `Ctrl+P` → «Зберегти як PDF»).

## Навіщо потрібен Git

Уяви, що над одним кодом одночасно працює кілька людей. Кожен додає зміни,
щось ламає, щось виправляє. Без системи контролю версій хаос неминучий.

Git — це «машина часу» для коду. Він дозволяє:

* зберігати історію змін (усі версії коду);
* працювати командою над одним проєктом;
* безпечно експериментувати в гілках;
* швидко «відкотитись», якщо щось зламалось.

## Головні думки уроку

1. **Git ≠ GitHub.** Git — двигун на твоєму комп'ютері, GitHub — гараж у хмарі.
2. **Три зони.** Working directory → staging area → repository. Кожна команда
   переносить зміни з однієї зони в наступну.
3. **Коміт — це знімок** стану проєкту з унікальним хешем, автором і датою.
4. **Спочатку `git status`.** Це найчастіша команда в роботі: вона завжди каже,
   де ти є і що робити далі.

## Швидкий старт (усе, що потрібно в перший день)

```bash
git --version                          # перевірити, що Git встановлено
git config --global user.name "Ім'я"   # хто автор комітів
git config --global user.email "mail@example.com"
git config --global init.defaultBranch main

mkdir my_project && cd my_project
git init                               # створити репозиторій
git status                             # що зараз відбувається

echo "print('Hello Git!')" > main.py
git add main.py                        # у staging
git commit -m "add main.py"            # зафіксувати
git log --oneline                      # історія
```

## Практика

Дивись [practice/PRACTICE.md](practice/PRACTICE.md) — крок за кроком створюємо
власний репозиторій-піщаницю і проходимо повний цикл змін.

## Домашнє завдання

Дивись [homework/HOMEWORK.md](homework/HOMEWORK.md).

## Додаткові матеріали

- [Завантажити Git](https://git-scm.com/downloads)
- [Pro Git — безкоштовна книга українською](https://git-scm.com/book/uk/v2)
- [Довідник команд Git](https://git-scm.com/docs)
- [Інтерактивний тренажер гілок](https://learngitbranching.js.org/?locale=uk)
- [Шпаргалка GitHub (PDF)](https://education.github.com/git-cheat-sheet-education.pdf)
- [Генератор .gitignore](https://www.toptal.com/developers/gitignore)
- [Oh Shit, Git!?! — як виправляти помилки](https://ohshitgit.com/)
