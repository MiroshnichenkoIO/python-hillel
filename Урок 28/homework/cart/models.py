from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from shop.models import Book


class CartModel(models.Model):
    """Кошик в базі."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name=_("користувач"),
    )
    created_at = models.DateTimeField(_("створено"), auto_now_add=True)

    class Meta:
        verbose_name = _("кошик")
        verbose_name_plural = _("кошики")

    def __str__(self) -> str:
        """Власник."""
        return str(self.user)

    def get_total_price(self) -> Decimal:
        """Сума."""
        return sum(
            (item.get_cost() for item in self.items.all()), Decimal("0")
        )


class CartItem(models.Model):
    """Рядок кошика."""

    cart = models.ForeignKey(
        CartModel,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("кошик"),
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name=_("книга"),
    )
    quantity = models.PositiveIntegerField(_("кількість"), default=1)

    class Meta:
        ordering = ["id"]
        verbose_name = _("рядок кошика")
        verbose_name_plural = _("рядки кошика")
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "book"], name="unique_cart_book"
            ),
        ]

    def __str__(self) -> str:
        """Рядок."""
        return f"{self.book} x {self.quantity}"

    def get_cost(self) -> Decimal:
        """Вартість."""
        return self.book.price * self.quantity
