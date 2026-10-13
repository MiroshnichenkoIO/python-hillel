"""Тестові дані: користувачі, групи, книги."""
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bookshop.settings")
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from django.contrib.auth.models import Group, Permission  # noqa: E402

from shop.models import Book, Category  # noqa: E402

User = get_user_model()

admin, created = User.objects.get_or_create(
    username="admin", defaults={"is_staff": True, "is_superuser": True}
)
if created:
    admin.set_password("admin")
    admin.save()
    print("створено суперкористувача admin / admin")

managers, _ = Group.objects.get_or_create(name="Менеджери")
managers.permissions.set(
    Permission.objects.filter(
        codename__in=["add_book", "change_book", "delete_book", "view_book"]
    )
)
buyers, _ = Group.objects.get_or_create(name="Покупці")
buyers.permissions.set(Permission.objects.filter(codename="view_book"))
print("групи: Менеджери, Покупці")

for username, group in (("manager", managers), ("buyer", buyers)):
    user, created = User.objects.get_or_create(username=username)
    if created:
        user.set_password("pass12345")
        user.save()
        user.groups.add(group)
        print(f"створено {username} / pass12345 ({group.name})")

if not Category.objects.exists():
    detektiv = Category.objects.create(name="Детектив", slug="detektiv")
    fentezi = Category.objects.create(name="Фентезі", slug="fentezi")

    Book.objects.create(
        title="Вбивство у «Східному експресі»", author="Агата Крісті",
        price=500, stock=3, category=detektiv,
    )
    Book.objects.create(
        title="Смерть на Нілі", author="Агата Крісті",
        price=450, stock=0, category=detektiv,
    )
    Book.objects.create(
        title="І не лишилось жодного", author="Агата Крісті",
        price=350, stock=7, category=detektiv,
    )
    Book.objects.create(
        title="Володар перснів", author="Джон Роналд Руел Толкін",
        price=700, stock=2, category=fentezi,
    )
    Book.objects.create(
        title="Хроніки Нарнії", author="Клайв Стейплз Льюїс",
        price=600, stock=0, category=fentezi,
    )
    print("створено 2 категорії та 5 книг")

print("книг у базі:", Book.objects.count())
