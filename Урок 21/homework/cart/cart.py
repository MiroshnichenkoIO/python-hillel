from copy import deepcopy
from decimal import Decimal
from typing import Iterator

from django.conf import settings
from django.http import HttpRequest

from shop.models import Book


class Cart:
    """Кошик."""

    def __init__(self, request: HttpRequest) -> None:
        """Кошик із сесії."""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(
        self, book: Book, quantity: int = 1, override_quantity: bool = False
    ) -> None:
        """Додати книгу."""
        book_id = str(book.id)
        if book_id not in self.cart:
            self.cart[book_id] = {"quantity": 0, "price": str(book.price)}
        if override_quantity:
            self.cart[book_id]["quantity"] = quantity
        else:
            self.cart[book_id]["quantity"] += quantity
        self.cart[book_id]["quantity"] = min(
            self.cart[book_id]["quantity"], book.stock
        )
        self.save()

    def remove(self, book: Book) -> None:
        """Прибрати книгу."""
        self.cart.pop(str(book.id), None)
        self.save()

    def clear(self) -> None:
        """Очистити."""
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def save(self) -> None:
        """Зберегти."""
        self.session.modified = True

    def __iter__(self) -> Iterator[dict]:
        """Рядки кошика."""
        books = Book.objects.filter(id__in=self.cart.keys())
        cart = deepcopy(self.cart)
        for book in books:
            cart[str(book.id)]["book"] = book
        for item in cart.values():
            if "book" not in item:
                continue
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["quantity"]
            yield item

    def __len__(self) -> int:
        """Кількість."""
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self) -> Decimal:
        """Сума."""
        return sum(
            (
                Decimal(item["price"]) * item["quantity"]
                for item in self.cart.values()
            ),
            Decimal("0"),
        )
