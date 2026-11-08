import logging

from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.db.models import Avg, Count, QuerySet, Sum
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from cart.forms import CartAddBookForm

from .models import Book, Category

logger = logging.getLogger("shop")


class BookListView(ListView):
    """Список книг."""

    model = Book
    paginate_by = 3

    def get_queryset(self) -> QuerySet:
        """Пошук."""
        books = Book.objects.order_by("title")

        q = self.request.GET.get("q")
        if q:
            books = books.filter(title__icontains=q)

        return books


class BookDetailView(DetailView):
    """Одна книга."""

    model = Book

    def get_context_data(self, **kwargs) -> dict:
        """Форма кошика."""
        context = super().get_context_data(**kwargs)
        context["cart_form"] = CartAddBookForm()
        return context


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


async def book_list_api(request: HttpRequest) -> JsonResponse:
    """Книги JSON."""
    books = Book.objects.order_by("title")
    q = request.GET.get("q")
    if q:
        books = books.filter(title__icontains=q)
    data = [
        book
        async for book in books.values(
            "id", "title", "author", "price", "stock", "category__name"
        )
    ]
    return JsonResponse({"count": len(data), "books": data})


async def book_detail_api(request: HttpRequest, pk: int) -> JsonResponse:
    """Книга JSON."""
    try:
        book = await Book.objects.select_related("category").aget(pk=pk)
    except Book.DoesNotExist:
        return JsonResponse({"error": _("Книгу не знайдено")}, status=404)
    return JsonResponse({
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "price": book.price,
        "stock": book.stock,
        "category": book.category.name,
    })


async def shop_stats_api(request: HttpRequest) -> JsonResponse:
    """Статистика."""
    books_count = await Book.objects.acount()
    totals = await Book.objects.aaggregate(
        avg_price=Avg("price"), total_stock=Sum("stock")
    )
    categories = [
        category
        async for category in Category.objects.annotate(
            books_count=Count("books")
        ).values("name", "books_count")
    ]
    return JsonResponse({
        "title": _("Статистика магазину"),
        "books_count": books_count,
        "avg_price": totals["avg_price"],
        "total_stock": totals["total_stock"] or 0,
        "categories": categories,
    })
