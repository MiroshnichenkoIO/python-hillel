import logging

from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.db.models import QuerySet
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .models import Book, Category

logger = logging.getLogger("shop")


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


class BookCreateView(
    LoginRequiredMixin, PermissionRequiredMixin, CreateView
):
    """Нова книга."""

    model = Book
    fields = ["title", "author", "category", "price", "stock", "description"]
    permission_required = "shop.add_book"

    def form_valid(self, form) -> HttpResponse:
        """Лог."""
        logger.info("%s додав книгу %s", self.request.user, form.instance)
        return super().form_valid(form)


class BookUpdateView(
    LoginRequiredMixin, PermissionRequiredMixin, UpdateView
):
    """Зміна книги."""

    model = Book
    fields = ["title", "author", "category", "price", "stock", "description"]
    permission_required = "shop.change_book"


class BookDeleteView(
    LoginRequiredMixin, PermissionRequiredMixin, DeleteView
):
    """Видалення книги."""

    model = Book
    success_url = reverse_lazy("shop:book_list")
    permission_required = "shop.delete_book"

    def form_valid(self, form) -> HttpResponse:
        """Лог."""
        logger.warning("%s видалив книгу %s", self.request.user, self.object)
        return super().form_valid(form)
