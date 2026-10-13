from django.db import models
from django.urls import reverse


class Category(models.Model):
    """Категорія книг."""

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self) -> str:
        """Назва категорії."""
        return self.name


class Book(models.Model):
    """Книга в магазині."""

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="books"
    )

    def __str__(self) -> str:
        """Назва книги."""
        return self.title

    def get_absolute_url(self) -> str:
        """Сторінка книги."""
        return reverse("shop:book_detail", kwargs={"pk": self.pk})
