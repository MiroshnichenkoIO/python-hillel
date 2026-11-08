from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from shop.models import Book

from .cart import Cart
from .forms import CartAddBookForm


@require_POST
def cart_add(request: HttpRequest, book_id: int) -> HttpResponse:
    """Додати."""
    cart = Cart(request)
    book = get_object_or_404(Book, id=book_id)
    form = CartAddBookForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            book=book,
            quantity=cd["quantity"],
            override_quantity=cd["override"],
        )
    return redirect("cart:cart_detail")


@require_POST
def cart_remove(request: HttpRequest, book_id: int) -> HttpResponse:
    """Прибрати."""
    cart = Cart(request)
    book = get_object_or_404(Book, id=book_id)
    cart.remove(book)
    return redirect("cart:cart_detail")


@require_POST
def cart_clear(request: HttpRequest) -> HttpResponse:
    """Очистити."""
    cart = Cart(request)
    cart.clear()
    return redirect("cart:cart_detail")


def cart_detail(request: HttpRequest) -> HttpResponse:
    """Кошик."""
    cart = Cart(request)
    return render(request, "cart/detail.html", {"cart": cart})
