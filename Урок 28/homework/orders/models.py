from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from shop.models import Book


class Order(models.Model):
    """Замовлення."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name=_("користувач"),
    )
    first_name = models.CharField(_("ім'я"), max_length=50)
    last_name = models.CharField(_("прізвище"), max_length=50)
    email = models.EmailField(_("email"))
    city = models.CharField(_("місто"), max_length=100)
    address = models.CharField(_("адреса"), max_length=250)
    created_at = models.DateTimeField(_("створено"), auto_now_add=True)
    paid = models.BooleanField(_("оплачено"), default=False)
    stripe_id = models.CharField(_("id у Stripe"), max_length=250, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("замовлення")
        verbose_name_plural = _("замовлення")

    def __str__(self) -> str:
        """Номер."""
        return _("Замовлення №%(id)s") % {"id": self.id}

    def get_total_cost(self) -> Decimal:
        """Сума."""
        return sum(
            (item.get_cost() for item in self.items.all()), Decimal("0")
        )


class OrderItem(models.Model):
    """Рядок замовлення."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("замовлення"),
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name=_("книга"),
    )
    price = models.DecimalField(_("ціна"), max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(_("кількість"), default=1)

    class Meta:
        verbose_name = _("рядок замовлення")
        verbose_name_plural = _("рядки замовлення")

    def __str__(self) -> str:
        """Рядок."""
        return f"{self.book} x {self.quantity}"

    def get_cost(self) -> Decimal:
        """Вартість."""
        return self.price * self.quantity
