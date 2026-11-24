from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class SignUpForm(UserCreationForm):
    """Реєстрація."""

    class Meta:
        model = CustomUser
        fields = ("username", "email", "phone")
