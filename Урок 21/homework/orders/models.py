from decimal import Decimal

from django.conf import settings
from django.db import models

from shop.models import Book


class Order(models.Model):
    """Замовлення."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    stripe_id = models.CharField(max_length=250, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Номер."""
        return f"Замовлення №{self.id}"

    def get_total_cost(self) -> Decimal:
        """Сума."""
        return sum(
            (item.get_cost() for item in self.items.all()), Decimal("0")
        )


class OrderItem(models.Model):
    """Рядок замовлення."""

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items"
    )
    book = models.ForeignKey(
        Book, on_delete=models.PROTECT, related_name="order_items"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self) -> str:
        """Рядок."""
        return f"{self.book} x {self.quantity}"

    def get_cost(self) -> Decimal:
        """Вартість."""
        return self.price * self.quantity
