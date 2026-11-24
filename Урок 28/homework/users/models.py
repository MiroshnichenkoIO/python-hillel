from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """Користувач."""

    phone = models.CharField(_("телефон"), max_length=20, blank=True)

    class Meta:
        verbose_name = _("користувач")
        verbose_name_plural = _("користувачі")

    def __str__(self) -> str:
        """Логін."""
        return self.username
