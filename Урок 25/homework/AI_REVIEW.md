# AI Code Review

Інструмент: Claude (Anthropic). Для рев'ю вибрано три найскладніші в'юхи
застосунку `orders` (`orders/views.py`): `order_create`, `payment_process`,
`stripe_webhook`. Промпти — у [AI_PROMPTS.md](AI_PROMPTS.md).

Позначки: ✅ застосовано, ❌ відхилено (з причиною).

---

## 1. `order_create` — оформлення замовлення

### Оригінальний код

```python
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
                messages.error(
                    request,
                    _("Недостатньо на складі: %(title)s") % {"title": error},
                )
                return redirect("cart:cart_detail")

            cart.clear()
            send_order_email(order)
            return redirect("orders:payment_process", order_id=order.id)
    else:
        form = OrderCreateForm()

    return render(request, "orders/create.html", {"cart": cart, "form": form})
```

### Рекомендації AI

| # | Рекомендація | Рішення |
| --- | --- | --- |
| 1 | `ValueError` як сигнал «немає на складі» перехоплює і будь-який інший `ValueError` усередині транзакції (наприклад, з `Decimal`), і покупець побачить хибне «недостатньо на складі». Потрібен свій виняток. | ✅ `OutOfStockError` |
| 2 | Книги блокуються по одній у порядку кошика. Два покупці з книгами A, B і B, A можуть заблокувати одне одного (deadlock на PostgreSQL). Блокувати всі книги одним запитом у стабільному порядку `id`. Заодно N запитів → 1. | ✅ `select_for_update().order_by("id").in_bulk(...)` |
| 3 | Якщо книгу видалили між читанням кошика і блокуванням, `.get()` дає `DoesNotExist` → 500. | ✅ `book is None` → `OutOfStockError`. Перевірка тестом показала: `Cart` сам пропускає видалені книги, тож 500 можливий лише в гонці — але обробка дешева |
| 4 | Після створення запам'ятати номер замовлення в сесії, щоб сторінка оплати могла перевірити власника (див. п. 2.1). | ✅ `request.session["order_id"]` |
| 5 | Відправку листа винести в Celery / `transaction.on_commit`, бо помилка SMTP дасть 500 після створення замовлення. | ❌ У проєкті console-backend, а лист і так відправляється **після** транзакції; Celery — окрема задача, не в цьому ДЗ |

### Фінальний код

```python
class OutOfStockError(Exception):
    """Немає на складі."""


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
```

---

## 2. `payment_process` — оплата через Stripe

### Оригінальний код

```python
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
```

### Рекомендації AI

| # | Рекомендація | Рішення |
| --- | --- | --- |
| 1 | **IDOR:** будь-хто, підставивши `/orders/process/1/`, `/2/`…, бачить чужі замовлення (склад, суму) і може створити для них оплату. Те саме в `payment_completed` / `payment_canceled`. Перевіряти власника: користувач замовлення або номер у сесії. | ✅ функція `get_user_order()` для всіх трьох в'юх, чуже → 404 |
| 2 | Вже оплачене замовлення можна «оплатити» ще раз — створюється нова сесія Stripe. | ✅ `if order.paid` → редирект на сторінку успіху |
| 3 | N+1: `order.items.all()` і `item.book.title` — окремий запит на кожну книгу (і в шаблоні теж). | ✅ `order.items.select_related("book")`, шаблон бере `items` з контексту |
| 4 | `client_reference_id` у Stripe — рядок; передавати `str(order.id)`. | ✅ |
| 5 | `int(item.price * 100)` замінити на `quantize`, щоб не втратити копійки. | ❌ Ціна — `DecimalField(decimal_places=2)`, множення `Decimal` на 100 завжди дає ціле; округлення не потрібне |

### Фінальний код

```python
def get_user_order(request: HttpRequest, order_id: int) -> Order:
    """Повертає замовлення, тільки якщо воно належить поточному покупцю."""
    order = get_object_or_404(Order, id=order_id)
    is_owner = request.user.is_authenticated and order.user == request.user
    if not is_owner and request.session.get("order_id") != order.id:
        raise Http404
    return order


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
```

---

## 3. `stripe_webhook` — підтвердження оплати

### Оригінальний код

```python
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
```

### Рекомендації AI

| # | Рекомендація | Рішення |
| --- | --- | --- |
| 1 | `session["client_reference_id"]` — `KeyError` → 500, якщо сесію створено не нашим сайтом (наприклад, тестова подія з `stripe trigger`). Stripe повторює подію при 500 до 3 днів. Брати через `.get()`. | ✅ |
| 2 | Оплати з відкладеним підтвердженням (банківський переказ) приходять подією `checkout.session.async_payment_succeeded` — її теж обробляти. | ✅ кортеж `PAID_EVENTS` |
| 3 | Оновлювати лише неоплачені (`paid=False`) і записувати в лог, яке замовлення оплачено, — щоб повтори подій не губили слід. | ✅ логер `orders` |
| 4 | Прибрати `@csrf_exempt` — це вразливість. | ❌ Хибна порада: Stripe не має CSRF-токена, захист вебхука — перевірка підпису `construct_event`, вона є |

### Фінальний код

```python
PAID_EVENTS = (
    "checkout.session.completed",
    "checkout.session.async_payment_succeeded",
)


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
```

---

## Перевірка

Нові тести на рекомендації — у `orders/tests.py`: `test_foreign_order_404`,
`test_owner_order`, `test_paid_order_redirect`, `test_deleted_book`,
`test_webhook_without_order`. Усі старі тести (кошик, транзакція, Stripe,
вебхук) пройшли без змін — **58 passed**.
