from django.conf import settings
from django.core.mail import send_mail

from .models import Order


def send_order_email(order: Order) -> None:
    """Лист покупцю."""
    message = (
        f"Вітаємо, {order.first_name}!\n\n"
        f"Ваше замовлення №{order.id} створено.\n"
        f"Сума: {order.get_total_cost()} грн.\n"
        f"Адреса: {order.city}, {order.address}"
    )
    send_mail(
        subject=f"Замовлення №{order.id}",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.email],
    )
