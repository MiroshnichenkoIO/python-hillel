from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from shop.models import Book, Category

from .models import Order, OrderItem

ORDER_DATA = {
    "first_name": "Ігор",
    "last_name": "Мірошниченко",
    "email": "igor@test.ua",
    "city": "Київ",
    "address": "вул. Хрещатик, 1",
}


class CartTests(TestCase):
    """Кошик."""

    def setUp(self) -> None:
        """Дані."""
        category = Category.objects.create(name="Детектив", slug="detektiv")
        self.book = Book.objects.create(
            title="Смерть на Нілі",
            author="Агата Крісті",
            price=450,
            stock=5,
            category=category,
        )

    def add(self, quantity: int) -> None:
        """Додати."""
        self.client.post(
            reverse("cart:cart_add", args=[self.book.id]),
            {"quantity": quantity},
        )

    def test_add(self) -> None:
        """Додавання."""
        self.add(2)
        self.add(1)
        cart = self.client.session["cart"]
        self.assertEqual(cart[str(self.book.id)]["quantity"], 3)

    def test_add_more_than_stock(self) -> None:
        """Не більше залишку."""
        self.add(10)
        cart = self.client.session["cart"]
        self.assertEqual(cart[str(self.book.id)]["quantity"], 5)

    def test_remove(self) -> None:
        """Видалення."""
        self.add(2)
        self.client.post(reverse("cart:cart_remove", args=[self.book.id]))
        self.assertEqual(self.client.session["cart"], {})

    def test_clear(self) -> None:
        """Очищення."""
        self.add(2)
        self.client.post(reverse("cart:cart_clear"))
        self.assertNotIn("cart", self.client.session)


class OrderTests(TestCase):
    """Замовлення."""

    def setUp(self) -> None:
        """Дані."""
        category = Category.objects.create(name="Детектив", slug="detektiv")
        self.book1 = Book.objects.create(
            title="Смерть на Нілі",
            author="Агата Крісті",
            price=450,
            stock=5,
            category=category,
        )
        self.book2 = Book.objects.create(
            title="Вбивство у Східному експресі",
            author="Агата Крісті",
            price=500,
            stock=3,
            category=category,
        )
        for book, quantity in ((self.book1, 2), (self.book2, 1)):
            self.client.post(
                reverse("cart:cart_add", args=[book.id]),
                {"quantity": quantity},
            )

    def test_empty_cart(self) -> None:
        """Порожній кошик."""
        self.client.post(reverse("cart:cart_clear"))
        response = self.client.get(reverse("orders:order_create"))
        self.assertRedirects(response, reverse("cart:cart_detail"))

    def test_create_order(self) -> None:
        """Нове замовлення."""
        response = self.client.post(
            reverse("orders:order_create"), ORDER_DATA
        )
        order = Order.objects.get()
        self.assertRedirects(
            response, reverse("orders:payment_process", args=[order.id])
        )
        self.assertEqual(order.items.count(), 2)
        self.assertEqual(order.get_total_cost(), 1400)
        self.assertFalse(self.client.session.get("cart"))
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.stock, 3)

    def test_order_user(self) -> None:
        """Замовлення користувача."""
        user = get_user_model().objects.create_user("buyer", "", "pass12345")
        self.client.force_login(user)
        self.client.post(
            reverse("cart:cart_add", args=[self.book1.id]), {"quantity": 1}
        )
        self.client.post(reverse("orders:order_create"), ORDER_DATA)
        self.assertEqual(Order.objects.get().user, user)

    def test_email(self) -> None:
        """Лист."""
        self.client.post(reverse("orders:order_create"), ORDER_DATA)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["igor@test.ua"])
        self.assertIn("1400", mail.outbox[0].body)

    def test_atomic_rollback(self) -> None:
        """Відкат."""
        Book.objects.filter(id=self.book2.id).update(stock=0)
        response = self.client.post(
            reverse("orders:order_create"), ORDER_DATA
        )
        self.assertRedirects(response, reverse("cart:cart_detail"))
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderItem.objects.count(), 0)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.stock, 5)
        self.assertEqual(len(mail.outbox), 0)

    @patch("orders.views.stripe.checkout.Session.create")
    def test_stripe_checkout(self, create) -> None:
        """Stripe Checkout."""
        create.return_value = SimpleNamespace(
            id="cs_test_1", url="https://checkout.stripe.com/c/pay/cs_test_1"
        )
        self.client.post(reverse("orders:order_create"), ORDER_DATA)
        order = Order.objects.get()
        response = self.client.post(
            reverse("orders:payment_process", args=[order.id])
        )
        self.assertRedirects(
            response, create.return_value.url, fetch_redirect_response=False
        )
        kwargs = create.call_args.kwargs
        self.assertEqual(kwargs["mode"], "payment")
        price_data = kwargs["line_items"][0]["price_data"]
        self.assertEqual(price_data["unit_amount"], 45000)
        order.refresh_from_db()
        self.assertEqual(order.stripe_id, "cs_test_1")

    @patch("orders.views.stripe.Webhook.construct_event")
    def test_webhook_paid(self, construct_event) -> None:
        """Вебхук."""
        self.client.post(reverse("orders:order_create"), ORDER_DATA)
        order = Order.objects.get()
        construct_event.return_value = {
            "type": "checkout.session.completed",
            "data": {"object": {
                "payment_status": "paid",
                "client_reference_id": str(order.id),
            }},
        }
        response = self.client.post(
            reverse("orders:stripe_webhook"), b"{}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertTrue(order.paid)

    def test_webhook_bad_signature(self) -> None:
        """Чужий підпис."""
        response = self.client.post(
            reverse("orders:stripe_webhook"), b"{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="t=1,v1=bad",
        )
        self.assertEqual(response.status_code, 400)

    def test_admin_inline(self) -> None:
        """Адмінка."""
        self.client.post(reverse("orders:order_create"), ORDER_DATA)
        order = Order.objects.get()
        admin = get_user_model().objects.create_superuser("admin", "", "admin")
        self.client.force_login(admin)
        response = self.client.get(
            reverse("admin:orders_order_change", args=[order.id])
        )
        self.assertContains(response, "Смерть на Нілі")
        self.assertContains(response, "items-TOTAL_FORMS")
