from decimal import Decimal

import pytest
from django.db import IntegrityError
from django.utils import translation

from shop.models import Book, Category
from shop.tests.factories import BookFactory, CategoryFactory


@pytest.mark.django_db
class TestCategory:
    """Категорія."""

    def test_str(self) -> None:
        """Назва."""
        # Generated with AI, reviewed and modified
        category = CategoryFactory(name="Поезія")
        assert str(category) == "Поезія"

    def test_slug_unique(self) -> None:
        """Унікальний слаг."""
        # Generated with AI, reviewed and modified
        CategoryFactory(slug="poetry")
        with pytest.raises(IntegrityError):
            CategoryFactory(slug="poetry")

    def test_books_related_name(self) -> None:
        """Книги категорії."""
        # Generated with AI, reviewed and modified
        category = CategoryFactory()
        BookFactory.create_batch(3, category=category)
        assert category.books.count() == 3

    def test_verbose_name(self) -> None:
        """Переклад."""
        # Generated with AI, reviewed and modified
        with translation.override("en"):
            assert Category._meta.verbose_name_plural == "categories"


@pytest.mark.django_db
class TestBook:
    """Книга."""

    def test_str(self) -> None:
        """Назва."""
        # Generated with AI, reviewed and modified
        assert str(BookFactory(title="Кобзар")) == "Кобзар"

    def test_absolute_url(self) -> None:
        """Посилання."""
        # Generated with AI, reviewed and modified
        book = BookFactory()
        assert book.get_absolute_url() == f"/books/{book.pk}/"

    def test_defaults(self) -> None:
        """Значення за замовчуванням."""
        # Generated with AI, reviewed and modified
        book = Book.objects.create(
            title="Енеїда",
            author="Іван Котляревський",
            price=Decimal("99.90"),
            category=CategoryFactory(),
        )
        assert book.stock == 0
        assert book.description == ""
        assert book.created_at is not None

    def test_price_decimal(self) -> None:
        """Ціна."""
        # Generated with AI, reviewed and modified
        book = BookFactory(price=Decimal("120.50"))
        book.refresh_from_db()
        assert book.price == Decimal("120.50")

    def test_cascade_delete(self) -> None:
        """Видалення з категорією."""
        # Generated with AI, reviewed and modified
        book = BookFactory()
        book.category.delete()
        assert not Book.objects.filter(pk=book.pk).exists()
