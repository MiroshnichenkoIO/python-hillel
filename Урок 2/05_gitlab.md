# 5. Підключення до GitLab

GitLab — це платформа для керування репозиторіями, CI/CD і DevOps-процесами.

Перевага GitLab у тому, що його можна встановити **на власному сервері** —
тобто повністю контролювати свій код. Саме тому GitLab часто обирають банки,
держкомпанії та великі корпорації.

## 1. Створення облікового запису

1. Перейди на <https://gitlab.com>
2. Зареєструйся або увійди за допомогою Google / GitHub
3. Натисни **New project** → **Create blank project**
4. Вкажи:
   * **Project name** (наприклад, `python-pro-lab`)
   * **Visibility** → `Private` або `Public`
   * зніми галочку `Initialize repository with a README` — локально файли вже є
5. Натисни **Create project**

## 2. Генерація SSH-ключів (якщо ще не створював)

```bash
ssh-keygen
```

Натискай `Enter` на всіх кроках. Після цього у теці `~/.ssh` з'являться файли:

* `id_rsa` → приватний ключ;
* `id_rsa.pub` → публічний ключ (його будемо копіювати).

Ключ один і той самий для GitHub, GitLab і будь-якого іншого сервісу —
генерувати новий не потрібно, якщо ти вже робив це для GitHub.

## 3. Додавання SSH-ключа у GitLab

1. Відкрий `id_rsa.pub` будь-яким текстовим редактором (або `cat ~/.ssh/id_rsa.pub`)
2. Скопіюй весь вміст (починається з `ssh-rsa...`)
3. У GitLab відкрий: **Profile → Preferences → SSH Keys → Add new key**
4. Встав ключ у поле та натисни **Add key**

Перевірка:

```bash
ssh -T git@gitlab.com
# Welcome to GitLab, @username!
```

## 4. Ініціалізація репозиторію та зв'язок із GitLab

Створи папку локально:

```bash
mkdir gitlab_test
cd gitlab_test
git init
```

Створи файл і зроби перший коміт:

```bash
echo "print('Hello GitLab!')" > main.py
git add .
git commit -m "initial commit"
```

Підключи віддалений репозиторій і відправ зміни:

```bash
git remote add origin git@gitlab.com:username/python-pro-lab.git
git push -u origin main
```

## GitHub vs GitLab — різниця в словах

Команди Git однакові, відрізняється лише термінологія інтерфейсу:

| GitHub | GitLab |
| --- | --- |
| Pull Request (PR) | Merge Request (MR) |
| Actions | CI/CD Pipelines |
| Organization | Group |
| Settings → SSH and GPG keys | Preferences → SSH Keys |

## Один проєкт — два remote

Можна тримати копію і там, і там:

```bash
git remote add github git@github.com:username/my_project.git
git remote add gitlab git@gitlab.com:username/my_project.git
git push github main
git push gitlab main
git remote -v          # перевірити список
```
