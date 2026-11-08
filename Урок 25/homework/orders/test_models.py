from datetime import timedelta
from decimal import Decimal

import pytest
from django.db.models import ProtectedError
from django.utils import timezone

from orders.models import Order, OrderItem
from shop.tests.factories import BookFactory, UserFactory

ORDER_DATA = {
    "first_name": "Ігор",
    "last_name": "Мірошниченко",
    "email": "igor@test.ua",
    "city": "Київ",
    "address": "вул. Хрещатик, 1",
}


@pytest.fixture
def order() -> Order:
    """Замовлення."""
    return Order.objects.create(**ORDER_DATA)


@pytest.mark.django_db
class TestOrder:
    """Замовлення."""

    def test_str(self, order) -> None:
        """Номер."""
        # Generated with AI, reviewed and modified
        assert str(order) == f"Замовлення №{order.id}"

    def test_defaults(self, order) -> None:
        """Значення за замовчуванням."""
        # Generated with AI, reviewed and modified
        assert order.paid is False
        assert order.stripe_id == ""
        assert order.user is None

    def test_total_cost_empty(self, order) -> None:
        """Порожнє замовлення."""
        # Generated with AI, reviewed and modified
        assert order.get_total_cost() == Decimal("0")

    def test_total_cost(self, order) -> None:
        """Сума."""
        # Generated with AI, reviewed and modified
        OrderItem.objects.create(
            order=order, book=BookFactory(), price=Decimal("450"), quantity=2
        )
        OrderItem.objects.create(
            order=order, book=BookFactory(), price=Decimal("99.50"), quantity=1
        )
        assert order.get_total_cost() == Decimal("999.50")

    def test_ordering(self) -> None:
        """Нові спочатку."""
        # Generated with AI, reviewed and modified
        old = Order.objects.create(**ORDER_DATA)
        Order.objects.filter(pk=old.pk).update(
            created_at=timezone.now() - timedelta(days=1)
        )
        new = Order.objects.create(**ORDER_DATA)
        assert list(Order.objects.all()) == [new, old]

    def test_user_set_null(self) -> None:
        """Видалення користувача."""
        # Generated with AI, reviewed and modified
        user = UserFactory()
        order = Order.objects.create(user=user, **ORDER_DATA)
        assert list(user.orders.all()) == [order]
        user.delete()
        order.refresh_from_db()
        assert order.user is None


@pytest.mark.django_db
class TestOrderItem:
    """Рядок замовлення."""

    def test_str(self, order) -> None:
        """Рядок."""
        # Generated with AI, reviewed and modified
        item = OrderItem.objects.create(
            order=order, book=BookFactory(title="Кобзар"), price=100,
            quantity=3,
        )
        assert str(item) == "Кобзар x 3"

    def test_cost(self, order) -> None:
        """Вартість."""
        # Generated with AI, reviewed and modified
        item = OrderItem(order=order, price=Decimal("120.50"), quantity=2)
        assert item.get_cost() == Decimal("241.00")

    def test_default_quantity(self, order) -> None:
        """Кількість."""
        # Generated with AI, reviewed and modified
        item = OrderItem.objects.create(
            order=order, book=BookFactory(), price=100
        )
        assert item.quantity == 1

    def test_book_protected(self, order) -> None:
        """Книгу не видалити."""
        # Generated with AI, reviewed and modified
        book = BookFactory()
        OrderItem.objects.create(order=order, book=book, price=100)
        with pytest.raises(ProtectedError):
            book.delete()

    def test_cascade_with_order(self, order) -> None:
        """Видалення з замовленням."""
        # Generated with AI, reviewed and modified
        OrderItem.objects.create(order=order, book=BookFactory(), price=100)
        order.delete()
        assert OrderItem.objects.count() == 0
