# 4. Підключення до GitHub і SSH-ключі

## Кроки підключення

1. Створи акаунт: <https://github.com>
2. Створи новий репозиторій → **New repository**
   (без `README`, без `.gitignore` — вони вже є локально, інакше буде конфлікт).
3. Скопіюй SSH-лінк, наприклад:

```
git@github.com:username/my_project.git
```

4. Додай віддалений репозиторій:

```bash
git remote add origin git@github.com:username/my_project.git
```

5. Відправ зміни:

```bash
git push -u origin main
```

Що тут що:

* `origin` — просто ім'я віддаленого репозиторію (домовленість, можна будь-яке);
* `main` — гілка, яку відправляємо;
* `-u` — запам'ятати зв'язок «локальна `main` ↔ `origin/main`». Після цього
  достатньо писати просто `git push` і `git pull`.

Перевірка:

```bash
git remote -v            # які remote підключені
git remote remove origin # відключити, якщо вказав неправильний
```

## Налаштування SSH-ключів (для безпечного підключення)

### Генерація ключів

```bash
ssh-keygen
```

Натискай `Enter` на всіх кроках (шлях за замовчуванням, без пароля —
для навчання так простіше).

Після цього в теці `~/.ssh` з'являться два файли:

* `id_rsa` — **приватний** ключ, нікому не показувати;
* `id_rsa.pub` — **публічний** ключ, його копіюємо в GitHub.

Сучасніший варіант (коротший і надійніший ключ):

```bash
ssh-keygen -t ed25519 -C "email@example.com"
# створить id_ed25519 та id_ed25519.pub
```

### Додати ключ у GitHub

**Settings → SSH and GPG keys → New SSH key**

Встав вміст `id_rsa.pub`.

Як подивитися вміст:

```bash
cat ~/.ssh/id_rsa.pub          # Git Bash / Linux / macOS
# ssh-rsa AAAAB3NzaC1yc2E... email@example.com
```

```powershell
Get-Content $env:USERPROFILE\.ssh\id_rsa.pub   # PowerShell
```

Копіюємо **весь рядок цілком**, від `ssh-rsa` (або `ssh-ed25519`) до кінця.

### Перевірка з'єднання

```bash
ssh -T git@github.com
# Hi username! You've successfully authenticated...
```

Перший раз запитає «Are you sure you want to continue connecting?» — відповідай `yes`.

## SSH проти HTTPS

| | SSH | HTTPS |
| --- | --- | --- |
| Лінк | `git@github.com:user/repo.git` | `https://github.com/user/repo.git` |
| Налаштування | один раз згенерувати ключ | нічого, але... |
| Кожен push | нічого не питає | питає токен (пароль з 2021 року не приймається) |

Для постійної роботи зручніший SSH — саме тому його й налаштовуємо.

## Часті помилки

| Помилка | Причина і що робити |
| --- | --- |
| `Permission denied (publickey)` | ключ не доданий у GitHub або доданий приватний замість `.pub` |
| `remote origin already exists` | remote уже є: `git remote set-url origin <новий лінк>` |
| `src refspec main does not match any` | немає жодного коміту або гілка називається `master` |
| `failed to push some refs` | у віддаленому репо є коміти, яких немає в тебе → спочатку `git pull` |
| `Repository not found` | помилка в назві або немає доступу до приватного репо |
