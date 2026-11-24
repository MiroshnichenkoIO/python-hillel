from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction

from shop.models import Book, Category


class Command(BaseCommand):
    help = "Заповнює магазин категоріями, книгами та користувачами"

    categories = [
        ("Детектив", "detektiv"),
        ("Фентезі", "fentezi"),
    ]

    books = [
        ("Вбивство у Східному експресі", "Агата Крісті", 500, 3, "detektiv"),
        ("Смерть на Нілі", "Агата Крісті", 450, 0, "detektiv"),
        ("І не лишилось жодного", "Агата Крісті", 350, 7, "detektiv"),
        ("Володар перснів", "Джон Толкін", 700, 2, "fentezi"),
        ("Хроніки Нарнії", "Клайв Льюїс", 600, 0, "fentezi"),
    ]

    @transaction.atomic
    def handle(self, *args, **options) -> None:
        """Заповнення."""
        category_objects = {}

        for name, slug in self.categories:
            category, _ = Category.objects.get_or_create(
                slug=slug, defaults={"name": name}
            )
            category_objects[slug] = category
        self.stdout.write(
            self.style.SUCCESS(f"Категорій: {len(category_objects)}")
        )

        created_books = 0

        for title, author, price, stock, slug in self.books:
            book, was_created = Book.objects.get_or_create(
                title=title,
                defaults={
                    "author": author,
                    "price": price,
                    "stock": stock,
                    "category": category_objects[slug],
                },
            )
            if was_created:
                created_books += 1
        self.stdout.write(self.style.SUCCESS(f"Створено книг: {created_books}"))

        managers, _ = Group.objects.get_or_create(name="Менеджери")
        managers.permissions.set(
            Permission.objects.filter(
                codename__in=["add_book", "change_book", "delete_book"]
            )
        )
        buyers, _ = Group.objects.get_or_create(name="Покупці")

        User = get_user_model()

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "", "admin")

        for username, group in (("manager", managers), ("buyer", buyers)):
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username, "", "pass12345")
                user.groups.add(group)

        self.stdout.write(
            self.style.SUCCESS(f"Користувачів: {User.objects.count()}")
        )
