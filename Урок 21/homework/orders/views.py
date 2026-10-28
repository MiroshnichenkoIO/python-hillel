import stripe
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from cart.cart import Cart
from shop.models import Book

from .forms import OrderCreateForm
from .models import Order, OrderItem
from .utils import send_order_email

stripe.api_key = settings.STRIPE_SECRET_KEY


def order_create(request: HttpRequest) -> HttpResponse:
    """Оформлення."""
    cart = Cart(request)
    if len(cart) == 0:
        return redirect("cart:cart_detail")

    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    if request.user.is_authenticated:
                        order.user = request.user
                    order.save()
                    for item in cart:
                        book = Book.objects.select_for_update().get(
                            id=item["book"].id
                        )
                        if book.stock < item["quantity"]:
                            raise ValueError(book.title)
                        OrderItem.objects.create(
                            order=order,
                            book=book,
                            price=item["price"],
                            quantity=item["quantity"],
                        )
                        book.stock -= item["quantity"]
                        book.save(update_fields=["stock"])
            except ValueError as error:
                messages.error(request, f"Недостатньо на складі: {error}")
                return redirect("cart:cart_detail")

            cart.clear()
            send_order_email(order)
            return redirect("orders:payment_process", order_id=order.id)
    else:
        form = OrderCreateForm()

    return render(request, "orders/create.html", {"cart": cart, "form": form})


def payment_process(request: HttpRequest, order_id: int) -> HttpResponse:
    """Оплата."""
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        success_url = request.build_absolute_uri(
            reverse("orders:payment_completed", args=[order.id])
        )
        cancel_url = request.build_absolute_uri(
            reverse("orders:payment_canceled", args=[order.id])
        )
        session_data = {
            "mode": "payment",
            "client_reference_id": order.id,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "line_items": [],
        }
        for item in order.items.all():
            session_data["line_items"].append({
                "price_data": {
                    "unit_amount": int(item.price * 100),
                    "currency": "uah",
                    "product_data": {"name": item.book.title},
                },
                "quantity": item.quantity,
            })
        try:
            session = stripe.checkout.Session.create(**session_data)
        except stripe.StripeError as error:
            return render(
                request, "orders/payment_error.html", {"error": str(error)}
            )
        order.stripe_id = session.id
        order.save(update_fields=["stripe_id"])
        return redirect(session.url)

    return render(request, "orders/process.html", {"order": order})


def payment_completed(request: HttpRequest, order_id: int) -> HttpResponse:
    """Успіх."""
    order = get_object_or_404(Order, id=order_id)
    return render(request, "orders/completed.html", {"order": order})


def payment_canceled(request: HttpRequest, order_id: int) -> HttpResponse:
    """Скасовано."""
    order = get_object_or_404(Order, id=order_id)
    return render(request, "orders/canceled.html", {"order": order})


@csrf_exempt
@require_POST
def stripe_webhook(request: HttpRequest) -> HttpResponse:
    """Вебхук."""
    try:
        event = stripe.Webhook.construct_event(
            request.body,
            request.META.get("HTTP_STRIPE_SIGNATURE"),
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except (ValueError, stripe.SignatureVerificationError):
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        if session["payment_status"] == "paid":
            Order.objects.filter(
                id=session["client_reference_id"]
            ).update(paid=True)

    return HttpResponse(status=200)
