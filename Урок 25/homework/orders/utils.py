from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import gettext as _

from .models import Order


def send_order_email(order: Order) -> None:
    """Лист покупцю."""
    message = _(
        "Вітаємо, %(name)s!\n\n"
        "Ваше замовлення №%(id)s створено.\n"
        "Сума: %(total)s грн.\n"
        "Адреса: %(city)s, %(address)s"
    ) % {
        "name": order.first_name,
        "id": order.id,
        "total": order.get_total_cost(),
        "city": order.city,
        "address": order.address,
    }
    send_mail(
        subject=_("Замовлення №%(id)s") % {"id": order.id},
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.email],
    )
