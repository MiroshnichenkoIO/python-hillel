from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    """Категорія книг."""

    name = models.CharField(_("назва"), max_length=200)
    slug = models.SlugField(_("слаг"), unique=True)

    class Meta:
        verbose_name = _("категорія")
        verbose_name_plural = _("категорії")

    def __str__(self) -> str:
        """Назва категорії."""
        return self.name


class Book(models.Model):
    """Книга в магазині."""

    title = models.CharField(_("назва"), max_length=200)
    author = models.CharField(_("автор"), max_length=100)
    price = models.DecimalField(_("ціна"), max_digits=10, decimal_places=2)
    description = models.TextField(_("опис"), blank=True)
    stock = models.PositiveIntegerField(_("залишок"), default=0)
    created_at = models.DateTimeField(_("створено"), auto_now_add=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="books",
        verbose_name=_("категорія"),
    )

    class Meta:
        verbose_name = _("книга")
        verbose_name_plural = _("книги")

    def __str__(self) -> str:
        """Назва книги."""
        return self.title

    def get_absolute_url(self) -> str:
        """Сторінка книги."""
        return reverse("shop:book_detail", kwargs={"pk": self.pk})
