from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Order


class OrderCreateForm(forms.ModelForm):
    """Оформлення."""

    class Meta:
        model = Order
        fields = ["first_name", "last_name", "email", "city", "address"]
        labels = {
            "first_name": _("Ім'я"),
            "last_name": _("Прізвище"),
            "email": "Email",
            "city": _("Місто"),
            "address": _("Адреса"),
        }
