import pytest

from shop.models import Book
from shop.tests.factories import BookFactory, UserFactory


@pytest.fixture
def book() -> Book:
    """Книга."""
    return BookFactory(title="Кобзар", author="Тарас Шевченко")


@pytest.fixture
def user_client(client):
    """Клієнт з входом."""
    user = UserFactory()
    client.force_login(user)
    client.user = user
    return client
