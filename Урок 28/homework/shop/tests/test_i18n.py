import pytest
from django.urls import reverse
from django.utils import translation

from cart.forms import CartAddBookForm
from orders.forms import OrderCreateForm
from orders.models import Order
from shop.models import Book


@pytest.mark.django_db
class TestPagesLanguage:
    """Мова сторінок."""

    def test_catalog_uk_default(self, client, book) -> None:
        """Українська."""
        response = client.get(reverse("shop:book_list"))
        content = response.content.decode()
        assert response.status_code == 200
        assert "Каталог книг" in content
        assert '<html lang="uk">' in content

    def test_catalog_en_header(self, client, book) -> None:
        """Англійська."""
        response = client.get(
            reverse("shop:book_list"), HTTP_ACCEPT_LANGUAGE="en"
        )
        content = response.content.decode()
        assert "Book catalog" in content
        assert "Page 1 of 1" in content
        assert "Каталог книг" not in content

    def test_set_language(self, client, book) -> None:
        """Перемикач."""
        url = reverse("shop:book_detail", args=[book.pk])
        response = client.post(
            reverse("set_language"), {"language": "en", "next": url}
        )
        assert response.status_code == 302
        response = client.get(response.url)
        content = response.content.decode()
        assert "Add to cart" in content
        assert "Author" in content

    def test_cart_en(self, client) -> None:
        """Кошик."""
        response = client.get(
            reverse("cart:cart_detail"), HTTP_ACCEPT_LANGUAGE="en"
        )
        assert "Your cart is empty" in response.content.decode()


class TestModelsAndForms:
    """Моделі та форми."""

    def test_verbose_name(self) -> None:
        """Моделі."""
        with translation.override("en"):
            assert Book._meta.verbose_name == "book"
            assert Book._meta.get_field("price").verbose_name == "price"
        with translation.override("uk"):
            assert Book._meta.verbose_name_plural == "книги"

    def test_form_labels(self) -> None:
        """Форми."""
        with translation.override("en"):
            assert OrderCreateForm().fields["city"].label == "City"
            assert CartAddBookForm().fields["quantity"].label == "Quantity"
        with translation.override("uk"):
            assert OrderCreateForm().fields["city"].label == "Місто"

    def test_order_str(self) -> None:
        """Номер."""
        order = Order(id=7)
        with translation.override("en"):
            assert str(order) == "Order #7"
        with translation.override("uk"):
            assert str(order) == "Замовлення №7"
