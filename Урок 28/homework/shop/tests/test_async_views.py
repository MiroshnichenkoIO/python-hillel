import inspect
from decimal import Decimal

import pytest
from django.urls import reverse

from orders import views as order_views
from orders.models import Order
from shop import views
from shop.tests.factories import BookFactory


def test_views_are_async() -> None:
    """Корутини."""
    assert inspect.iscoroutinefunction(views.book_list_api)
    assert inspect.iscoroutinefunction(views.book_detail_api)
    assert inspect.iscoroutinefunction(views.shop_stats_api)
    assert inspect.iscoroutinefunction(order_views.my_orders_api)


@pytest.mark.django_db
class TestBookApi:
    """Книги."""

    def test_list(self, client, book) -> None:
        """Список."""
        BookFactory(title="Енеїда")
        response = client.get(reverse("shop:book_list_api"))
        data = response.json()
        assert response.status_code == 200
        assert data["count"] == 2
        assert data["books"][0]["title"] == "Енеїда"

    def test_search(self, client, book) -> None:
        """Пошук."""
        BookFactory(title="Енеїда")
        response = client.get(reverse("shop:book_list_api"), {"q": "Кобз"})
        assert response.json()["count"] == 1

    def test_detail(self, client, book) -> None:
        """Одна книга."""
        response = client.get(reverse("shop:book_detail_api", args=[book.pk]))
        data = response.json()
        assert data["author"] == "Тарас Шевченко"
        assert data["price"] == "100.00"
        assert data["category"] == book.category.name

    def test_detail_404(self, client) -> None:
        """Немає книги."""
        url = reverse("shop:book_detail_api", args=[999])
        response = client.get(url)
        assert response.status_code == 404
        assert response.json()["error"] == "Книгу не знайдено"
        response = client.get(url, HTTP_ACCEPT_LANGUAGE="en")
        assert response.json()["error"] == "Book not found"

    def test_stats(self, client, book) -> None:
        """Статистика."""
        BookFactory(category=book.category, price="200.00", stock=3)
        response = client.get(
            reverse("shop:shop_stats_api"), HTTP_ACCEPT_LANGUAGE="en"
        )
        data = response.json()
        assert data["title"] == "Shop statistics"
        assert data["books_count"] == 2
        assert Decimal(data["avg_price"]) == Decimal("150")
        assert data["total_stock"] == 8
        assert data["categories"] == [
            {"name": book.category.name, "books_count": 2}
        ]


@pytest.mark.django_db
class TestMyOrdersApi:
    """Мої замовлення."""

    def test_guest(self, client) -> None:
        """Гість."""
        response = client.get(reverse("orders:my_orders_api"))
        assert response.status_code == 401

    def test_user_orders(self, user_client) -> None:
        """Лише свої."""
        data = {
            "first_name": "Ihor", "last_name": "M", "email": "a@a.com",
            "city": "Kyiv", "address": "Street 1",
        }
        order = Order.objects.create(user=user_client.user, **data)
        Order.objects.create(**data)
        response = user_client.get(reverse("orders:my_orders_api"))
        result = response.json()
        assert result["count"] == 1
        assert result["orders"][0]["id"] == order.id
        assert result["orders"][0]["title"] == f"Замовлення №{order.id}"
