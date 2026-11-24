from decimal import Decimal
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient, APITestCase
from rest_framework.throttling import AnonRateThrottle

from api.permissions import IsOwnerOrReadOnly
from cart.models import CartItem, CartModel
from orders.models import Order, OrderItem
from shop.models import Book, Category

User = get_user_model()

ORDER_DATA = {
    "first_name": "Іван",
    "last_name": "Петренко",
    "email": "ivan@example.com",
    "city": "Київ",
    "address": "Хрещатик, 1",
}


class BaseAPITestCase(APITestCase):
    """Спільні дані."""

    def setUp(self) -> None:
        """Дані."""
        cache.clear()
        self.client = APIClient()
        self.category = Category.objects.create(name="Поезія", slug="poetry")
        self.prose = Category.objects.create(name="Проза", slug="prose")
        self.kobzar = Book.objects.create(
            title="Кобзар",
            author="Тарас Шевченко",
            price=Decimal("250.00"),
            stock=5,
            category=self.category,
        )
        self.zakhar = Book.objects.create(
            title="Захар Беркут",
            author="Іван Франко",
            price=Decimal("300.00"),
            stock=0,
            category=self.prose,
        )
        self.user = User.objects.create_user(
            username="buyer", password="secret-pass-123"
        )
        self.other = User.objects.create_user(
            username="other", password="secret-pass-123"
        )
        self.admin = User.objects.create_user(
            username="admin", password="secret-pass-123", is_staff=True
        )

    def make_order(self, user, paid: bool = False) -> Order:
        """Замовлення."""
        order = Order.objects.create(user=user, paid=paid, **ORDER_DATA)
        OrderItem.objects.create(
            order=order, book=self.kobzar, price=Decimal("250.00"), quantity=2
        )
        return order


class JWTTests(BaseAPITestCase):
    """JWT."""

    def get_tokens(self) -> dict:
        """Токени."""
        response = self.client.post(
            "/api/token/",
            {"username": "buyer", "password": "secret-pass-123"},
            format="json",
        )
        return response.data

    def test_obtain_token(self) -> None:
        """Отримати токен."""
        tokens = self.get_tokens()
        self.assertIn("access", tokens)
        self.assertIn("refresh", tokens)

    def test_wrong_password(self) -> None:
        """Невірний пароль."""
        response = self.client.post(
            "/api/token/",
            {"username": "buyer", "password": "wrong"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_refresh_token(self) -> None:
        """Оновити токен."""
        tokens = self.get_tokens()
        response = self.client.post(
            "/api/token/refresh/",
            {"refresh": tokens["refresh"]},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    def test_verify_token(self) -> None:
        """Перевірити токен."""
        tokens = self.get_tokens()
        response = self.client.post(
            "/api/token/verify/", {"token": tokens["access"]}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            "/api/token/verify/", {"token": "bad.token"}, format="json"
        )
        self.assertEqual(response.status_code, 401)

    def test_access_with_bearer(self) -> None:
        """Доступ з Bearer."""
        tokens = self.get_tokens()
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {tokens['access']}"
        )
        response = self.client.get("/api/cart/")
        self.assertEqual(response.status_code, 200)


class CategoryTests(BaseAPITestCase):
    """Категорії."""

    def test_list_is_public(self) -> None:
        """Список для всіх."""
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(response.data["results"][0]["books_count"], 1)

    def test_detail_has_nested_books(self) -> None:
        """Книги всередині."""
        response = self.client.get("/api/categories/poetry/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["books"][0]["title"], "Кобзар")

    def test_create_only_admin(self) -> None:
        """Створює лише адмін."""
        data = {"name": "Історія", "slug": "history"}
        self.client.force_authenticate(self.user)
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, 403)
        self.client.force_authenticate(self.admin)
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Category.objects.filter(slug="history").exists())


class BookTests(BaseAPITestCase):
    """Книги."""

    def test_list_is_public(self) -> None:
        """Список для всіх."""
        response = self.client.get("/api/books/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)

    def test_nested_category(self) -> None:
        """Категорія всередині."""
        response = self.client.get(f"/api/books/{self.kobzar.pk}/")
        self.assertEqual(response.data["category"]["slug"], "poetry")

    def test_pagination_20(self) -> None:
        """20 на сторінці."""
        for number in range(25):
            Book.objects.create(
                title=f"Книга {number}",
                author="Автор",
                price=Decimal("10.00"),
                category=self.category,
            )
        response = self.client.get("/api/books/")
        self.assertEqual(response.data["count"], 27)
        self.assertEqual(len(response.data["results"]), 20)
        self.assertIsNotNone(response.data["next"])
        response = self.client.get("/api/books/?page=2")
        self.assertEqual(len(response.data["results"]), 7)

    def test_filter_by_category(self) -> None:
        """Фільтр за категорією."""
        response = self.client.get("/api/books/?category=prose")
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Захар Беркут")

    def test_filter_by_price(self) -> None:
        """Фільтр за ціною."""
        response = self.client.get("/api/books/?min_price=260")
        self.assertEqual(response.data["count"], 1)
        response = self.client.get("/api/books/?max_price=260")
        self.assertEqual(response.data["results"][0]["title"], "Кобзар")

    def test_filter_in_stock(self) -> None:
        """Є на складі."""
        response = self.client.get("/api/books/?in_stock=true")
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Кобзар")

    def test_search_and_ordering(self) -> None:
        """Пошук і сортування."""
        response = self.client.get("/api/books/?search=Франко")
        self.assertEqual(response.data["count"], 1)
        response = self.client.get("/api/books/?ordering=-price")
        self.assertEqual(response.data["results"][0]["title"], "Захар Беркут")

    def test_anonymous_can_not_create(self) -> None:
        """Гість не створює."""
        response = self.client.post(
            "/api/books/", {"title": "Нова"}, format="json"
        )
        self.assertEqual(response.status_code, 401)

    def test_user_can_not_delete(self) -> None:
        """Покупець не видаляє."""
        self.client.force_authenticate(self.user)
        response = self.client.delete(f"/api/books/{self.kobzar.pk}/")
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Book.objects.filter(pk=self.kobzar.pk).exists())

    def test_admin_create_and_update(self) -> None:
        """Адмін створює і змінює."""
        self.client.force_authenticate(self.admin)
        data = {
            "title": "Лісова пісня",
            "author": "Леся Українка",
            "price": "180.00",
            "stock": 3,
            "category_id": self.category.pk,
        }
        response = self.client.post("/api/books/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["category"]["name"], "Поезія")
        response = self.client.patch(
            f"/api/books/{response.data['id']}/",
            {"price": "200.00"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["price"], "200.00")

    def test_negative_price(self) -> None:
        """Від'ємна ціна."""
        self.client.force_authenticate(self.admin)
        response = self.client.patch(
            f"/api/books/{self.kobzar.pk}/", {"price": "-5"}, format="json"
        )
        self.assertEqual(response.status_code, 400)


class CartTests(BaseAPITestCase):
    """Кошик."""

    def setUp(self) -> None:
        """Дані."""
        super().setUp()
        self.client.force_authenticate(self.user)

    def test_anonymous_has_no_cart(self) -> None:
        """Гість без кошика."""
        self.client.force_authenticate(None)
        response = self.client.get("/api/cart/")
        self.assertEqual(response.status_code, 401)

    def test_add_item(self) -> None:
        """Додати книгу."""
        response = self.client.post(
            "/api/cart/items/",
            {"book_id": self.kobzar.pk, "quantity": 2},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["book"]["title"], "Кобзар")
        self.assertEqual(response.data["cost"], "500.00")

    def test_add_same_book_twice(self) -> None:
        """Та сама книга."""
        for _ in range(2):
            self.client.post(
                "/api/cart/items/",
                {"book_id": self.kobzar.pk, "quantity": 2},
                format="json",
            )
        self.assertEqual(CartItem.objects.count(), 1)
        self.assertEqual(CartItem.objects.get().quantity, 4)

    def test_quantity_over_stock(self) -> None:
        """Більше ніж є."""
        response = self.client.post(
            "/api/cart/items/",
            {"book_id": self.kobzar.pk, "quantity": 10},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("quantity", response.data)

    def test_cart_total(self) -> None:
        """Сума кошика."""
        self.client.post(
            "/api/cart/items/",
            {"book_id": self.kobzar.pk, "quantity": 3},
            format="json",
        )
        response = self.client.get("/api/cart/")
        self.assertEqual(response.data["total_price"], "750.00")
        self.assertEqual(len(response.data["items"]), 1)

    def test_change_quantity(self) -> None:
        """Змінити кількість."""
        response = self.client.post(
            "/api/cart/items/", {"book_id": self.kobzar.pk}, format="json"
        )
        response = self.client.patch(
            f"/api/cart/items/{response.data['id']}/",
            {"quantity": 4},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["quantity"], 4)

    def test_other_user_item_hidden(self) -> None:
        """Чужий рядок."""
        cart = CartModel.objects.create(user=self.other)
        item = CartItem.objects.create(cart=cart, book=self.kobzar)
        response = self.client.delete(f"/api/cart/items/{item.pk}/")
        self.assertEqual(response.status_code, 404)
        self.assertTrue(CartItem.objects.filter(pk=item.pk).exists())

    def test_clear(self) -> None:
        """Очистити."""
        self.client.post(
            "/api/cart/items/", {"book_id": self.kobzar.pk}, format="json"
        )
        response = self.client.delete("/api/cart/clear/")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(CartItem.objects.count(), 0)


class OrderTests(BaseAPITestCase):
    """Замовлення."""

    def setUp(self) -> None:
        """Дані."""
        super().setUp()
        self.client.force_authenticate(self.user)

    def add_to_cart(self, quantity: int) -> None:
        """У кошик."""
        cart, _ = CartModel.objects.get_or_create(user=self.user)
        CartItem.objects.create(
            cart=cart, book=self.kobzar, quantity=quantity
        )

    def test_anonymous_forbidden(self) -> None:
        """Гість без замовлень."""
        self.client.force_authenticate(None)
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, 401)

    def test_create_from_cart(self) -> None:
        """Замовлення з кошика."""
        self.add_to_cart(2)
        response = self.client.post("/api/orders/", ORDER_DATA, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["user"], "buyer")
        self.assertEqual(response.data["total_cost"], "500.00")
        self.assertEqual(response.data["items"][0]["book"]["title"], "Кобзар")
        self.kobzar.refresh_from_db()
        self.assertEqual(self.kobzar.stock, 3)
        self.assertEqual(CartItem.objects.count(), 0)

    def test_empty_cart(self) -> None:
        """Порожній кошик."""
        response = self.client.post("/api/orders/", ORDER_DATA, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)

    def test_not_enough_stock(self) -> None:
        """Не вистачає."""
        self.add_to_cart(2)
        Book.objects.filter(pk=self.kobzar.pk).update(stock=1)
        response = self.client.post("/api/orders/", ORDER_DATA, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(CartItem.objects.count(), 1)

    def test_invalid_email(self) -> None:
        """Поганий email."""
        self.add_to_cart(1)
        data = {**ORDER_DATA, "email": "not-email"}
        response = self.client.post("/api/orders/", data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_list_only_own(self) -> None:
        """Лише свої."""
        self.make_order(self.user)
        self.make_order(self.other)
        response = self.client.get("/api/orders/")
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["user"], "buyer")

    def test_other_order_not_found(self) -> None:
        """Чуже замовлення."""
        order = self.make_order(self.other)
        response = self.client.get(f"/api/orders/{order.pk}/")
        self.assertEqual(response.status_code, 404)

    def test_admin_sees_all(self) -> None:
        """Адмін бачить усі."""
        self.make_order(self.user)
        self.make_order(self.other)
        self.client.force_authenticate(self.admin)
        response = self.client.get("/api/orders/")
        self.assertEqual(response.data["count"], 2)

    def test_owner_changes_address(self) -> None:
        """Власник змінює адресу."""
        order = self.make_order(self.user)
        response = self.client.patch(
            f"/api/orders/{order.pk}/", {"city": "Львів"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["city"], "Львів")

    def test_paid_not_editable_by_user(self) -> None:
        """Оплату не змінити."""
        order = self.make_order(self.user)
        self.client.patch(
            f"/api/orders/{order.pk}/", {"paid": True}, format="json"
        )
        order.refresh_from_db()
        self.assertFalse(order.paid)

    def test_paid_order_locked(self) -> None:
        """Оплачене не змінюється."""
        order = self.make_order(self.user, paid=True)
        response = self.client.patch(
            f"/api/orders/{order.pk}/", {"city": "Львів"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        response = self.client.delete(f"/api/orders/{order.pk}/")
        self.assertEqual(response.status_code, 400)

    def test_cancel_returns_stock(self) -> None:
        """Скасування повертає залишок."""
        order = self.make_order(self.user)
        response = self.client.delete(f"/api/orders/{order.pk}/")
        self.assertEqual(response.status_code, 204)
        self.kobzar.refresh_from_db()
        self.assertEqual(self.kobzar.stock, 7)
        self.assertFalse(Order.objects.filter(pk=order.pk).exists())

    def test_mark_paid_only_admin(self) -> None:
        """Оплату ставить адмін."""
        order = self.make_order(self.user)
        url = f"/api/orders/{order.pk}/mark_paid/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)
        self.client.force_authenticate(self.admin)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["paid"])

    def test_filter_paid(self) -> None:
        """Фільтр оплати."""
        self.make_order(self.user)
        self.make_order(self.user, paid=True)
        response = self.client.get("/api/orders/?paid=true")
        self.assertEqual(response.data["count"], 1)
        self.assertTrue(response.data["results"][0]["paid"])


class PermissionTests(BaseAPITestCase):
    """IsOwnerOrReadOnly."""

    def test_owner_or_read_only(self) -> None:
        """Власник і адмін."""
        order = self.make_order(self.user)
        permission = IsOwnerOrReadOnly()
        cases = [
            ("GET", self.other, True),
            ("PATCH", self.other, False),
            ("PATCH", self.user, True),
            ("DELETE", self.admin, True),
        ]
        for method, user, expected in cases:
            request = Mock(method=method, user=user)
            self.assertEqual(
                permission.has_object_permission(request, None, order),
                expected,
                method,
            )


class ThrottleTests(BaseAPITestCase):
    """Тротлінг."""

    def test_anon_throttled(self) -> None:
        """Ліміт для гостя."""
        with patch.object(
            AnonRateThrottle, "THROTTLE_RATES", {"anon": "3/minute"}
        ):
            for _ in range(3):
                response = self.client.get("/api/books/")
                self.assertEqual(response.status_code, 200)
            response = self.client.get("/api/books/")
        self.assertEqual(response.status_code, 429)


class DocsAndCorsTests(BaseAPITestCase):
    """Документація і CORS."""

    def test_docs_page(self) -> None:
        """Сторінка документації."""
        response = self.client.get("/api/docs/")
        self.assertEqual(response.status_code, 200)

    def test_schema(self) -> None:
        """Схема OpenAPI."""
        response = self.client.get("/api/schema/?format=json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("/api/books/", response.json()["paths"])

    def test_cors_header(self) -> None:
        """Заголовок CORS."""
        response = self.client.get(
            "/api/books/", HTTP_ORIGIN="http://localhost:3000"
        )
        self.assertEqual(
            response["Access-Control-Allow-Origin"], "http://localhost:3000"
        )
        response = self.client.get(
            "/api/books/", HTTP_ORIGIN="http://evil.example.com"
        )
        self.assertNotIn("Access-Control-Allow-Origin", response)
