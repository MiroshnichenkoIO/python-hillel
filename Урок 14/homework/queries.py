"""ORM-запити до магазину книг. Запуск: python queries.py"""
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bookshop.settings")
django.setup()

from django.db.models import Count, Q, QuerySet  # noqa: E402

from shop.models import Book, Category  # noqa: E402


def show(title: str, qs: QuerySet) -> None:
    """Друкує заголовок, SQL і результат."""
    print(f"\n=== {title} ===")
    print("SQL:", qs.query)
    for obj in qs:
        print(" -", obj)


def cheap_books(limit: int) -> QuerySet:
    """Книги дешевші за limit."""
    return Book.objects.filter(price__lt=limit)


def books_in_stock() -> QuerySet:
    """Книги в наявності."""
    return Book.objects.filter(stock__gt=0)


def books_by_category(slug: str) -> QuerySet:
    """Книги з категорії."""
    return Book.objects.filter(category__slug=slug)


def categories_with_count() -> QuerySet:
    """Категорії з кількістю книг."""
    return Category.objects.annotate(total=Count("books")).order_by("-total")


def books_by_author_or_cheap(author: str, limit: int) -> QuerySet:
    """Книги автора або дешевші за limit."""
    return Book.objects.filter(Q(author__icontains=author) | Q(price__lt=limit))


def books_in_stock_except(author: str) -> QuerySet:
    """Книги в наявності, крім книг автора."""
    return Book.objects.filter(stock__gt=0).filter(~Q(author__icontains=author))


if __name__ == "__main__":
    show("filter: дешевші за 500", cheap_books(500))
    show("filter: є в наявності", books_in_stock())
    show("filter: категорія fentezi", books_by_category("fentezi"))

    print("\n=== annotate: книг у категорії ===")
    for category in categories_with_count():
        print(f" - {category.name}: {category.total}")

    show("Q: Крісті або дешевші за 650", books_by_author_or_cheap("Крісті", 650))
    show("Q: в наявності, крім Крісті", books_in_stock_except("Крісті"))
