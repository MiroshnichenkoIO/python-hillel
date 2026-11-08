import logging

from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import SignUpForm

logger = logging.getLogger("users")


class SignUpView(CreateView):
    """Реєстрація."""

    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("shop:book_list")

    def form_valid(self, form: SignUpForm) -> HttpResponse:
        """Група та вхід."""
        response = super().form_valid(form)
        group, _ = Group.objects.get_or_create(name="Покупці")
        self.object.groups.add(group)
        login(self.request, self.object)
        logger.info("Новий користувач: %s", self.object.username)
        return response
