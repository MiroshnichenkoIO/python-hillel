from django.db.models import QuerySet
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .models import Book, Category


class BookListView(ListView):
    """Список книг."""

    model = Book
    paginate_by = 3

    def get_queryset(self) -> QuerySet:
        """Фільтри."""
        books = Book.objects.order_by("title")

        q = self.request.GET.get("q")
        if q:
            books = books.filter(title__icontains=q)

        category = self.request.GET.get("category")
        if category:
            books = books.filter(category__slug=category)

        if self.request.GET.get("in_stock"):
            books = books.filter(stock__gt=0)

        return books

    def get_context_data(self, **kwargs) -> dict:
        """Категорії."""
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        return context


class BookDetailView(DetailView):
    """Одна книга."""

    model = Book


class BookCreateView(CreateView):
    """Нова книга."""

    model = Book
    fields = ["title", "author", "category", "price", "stock", "description"]


class BookUpdateView(UpdateView):
    """Зміна книги."""

    model = Book
    fields = ["title", "author", "category", "price", "stock", "description"]


class BookDeleteView(DeleteView):
    """Видалення книги."""

    model = Book
    success_url = reverse_lazy("shop:book_list")
