import logging

import stripe
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from cart.cart import Cart
from shop.models import Book

from .forms import OrderCreateForm
from .models import Order, OrderItem
from .utils import send_order_email

stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger("orders")

PAID_EVENTS = (
    "checkout.session.completed",
    "checkout.session.async_payment_succeeded",
)


class OutOfStockError(Exception):
    """Немає на складі."""


def get_user_order(request: HttpRequest, order_id: int) -> Order:
    """Повертає замовлення, тільки якщо воно належить поточному покупцю."""
    order = get_object_or_404(Order, id=order_id)
    is_owner = request.user.is_authenticated and order.user == request.user
    if not is_owner and request.session.get("order_id") != order.id:
        raise Http404
    return order


def order_create(request: HttpRequest) -> HttpResponse:
    """Оформлює замовлення з кошика і списує залишки в одній транзакції."""
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
                    locked = Book.objects.select_for_update().order_by("id")
                    books = locked.in_bulk([item["book"].id for item in cart])
                    for item in cart:
                        book = books.get(item["book"].id)
                        if book is None or book.stock < item["quantity"]:
                            raise OutOfStockError(item["book"].title)
                        OrderItem.objects.create(
                            order=order,
                            book=book,
                            price=item["price"],
                            quantity=item["quantity"],
                        )
                        book.stock -= item["quantity"]
                        book.save(update_fields=["stock"])
            except OutOfStockError as error:
                messages.error(
                    request,
                    _("Недостатньо на складі: %(title)s") % {"title": error},
                )
                return redirect("cart:cart_detail")

            cart.clear()
            request.session["order_id"] = order.id
            send_order_email(order)
            return redirect("orders:payment_process", order_id=order.id)
    else:
        form = OrderCreateForm()

    return render(request, "orders/create.html", {"cart": cart, "form": form})


def payment_process(request: HttpRequest, order_id: int) -> HttpResponse:
    """Показує сторінку оплати, а на POST створює сесію Stripe Checkout."""
    order = get_user_order(request, order_id)
    if order.paid:
        return redirect("orders:payment_completed", order_id=order.id)

    items = order.items.select_related("book")
    if request.method == "POST":
        success_url = request.build_absolute_uri(
            reverse("orders:payment_completed", args=[order.id])
        )
        cancel_url = request.build_absolute_uri(
            reverse("orders:payment_canceled", args=[order.id])
        )
        session_data = {
            "mode": "payment",
            "client_reference_id": str(order.id),
            "success_url": success_url,
            "cancel_url": cancel_url,
            "line_items": [],
        }
        for item in items:
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

    return render(
        request, "orders/process.html", {"order": order, "items": items}
    )


def payment_completed(request: HttpRequest, order_id: int) -> HttpResponse:
    """Сторінка, куди Stripe повертає покупця після успішної оплати."""
    order = get_user_order(request, order_id)
    return render(request, "orders/completed.html", {"order": order})


def payment_canceled(request: HttpRequest, order_id: int) -> HttpResponse:
    """Сторінка, куди Stripe повертає покупця, якщо оплату скасовано."""
    order = get_user_order(request, order_id)
    return render(request, "orders/canceled.html", {"order": order})


@csrf_exempt
@require_POST
def stripe_webhook(request: HttpRequest) -> HttpResponse:
    """Приймає подію від Stripe, перевіряє підпис і позначає оплату."""
    try:
        event = stripe.Webhook.construct_event(
            request.body,
            request.META.get("HTTP_STRIPE_SIGNATURE"),
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except (ValueError, stripe.SignatureVerificationError):
        return HttpResponse(status=400)

    if event["type"] in PAID_EVENTS:
        session = event["data"]["object"]
        order_id = session.get("client_reference_id")
        if order_id and session.get("payment_status") == "paid":
            updated = Order.objects.filter(
                id=order_id, paid=False
            ).update(paid=True)
            if updated:
                logger.info("Замовлення %s оплачено", order_id)

    return HttpResponse(status=200)


async def my_orders_api(request: HttpRequest) -> JsonResponse:
    """Асинхронно повертає JSON зі списком замовлень поточного користувача."""
    user = await request.auser()
    if not user.is_authenticated:
        return JsonResponse({"error": _("Потрібно увійти")}, status=401)
    orders = [
        {
            "id": order.id,
            "title": str(order),
            "paid": order.paid,
            "created_at": order.created_at,
        }
        async for order in Order.objects.filter(user=user)
    ]
    return JsonResponse({"count": len(orders), "orders": orders})
