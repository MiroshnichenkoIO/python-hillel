from decimal import Decimal

import factory
from django.contrib.auth import get_user_model

from shop.models import Book, Category

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Користувач."""

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")


class CategoryFactory(factory.django.DjangoModelFactory):
    """Категорія."""

    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Категорія {n}")
    slug = factory.Sequence(lambda n: f"category-{n}")


class BookFactory(factory.django.DjangoModelFactory):
    """Книга."""

    class Meta:
        model = Book

    title = factory.Sequence(lambda n: f"Книга {n}")
    author = "Іван Франко"
    price = Decimal("100.00")
    stock = 5
    category = factory.SubFactory(CategoryFactory)
