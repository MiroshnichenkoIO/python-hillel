from django import forms

from .models import Order


class OrderCreateForm(forms.ModelForm):
    """Оформлення."""

    class Meta:
        model = Order
        fields = ["first_name", "last_name", "email", "city", "address"]
        labels = {
            "first_name": "Ім'я",
            "last_name": "Прізвище",
            "email": "Email",
            "city": "Місто",
            "address": "Адреса",
        }
