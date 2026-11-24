from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse

from .models import CustomUser


class AuthTests(TestCase):
    """Авторизація."""

    def setUp(self) -> None:
        """Дані."""
        managers = Group.objects.create(name="Менеджери")
        managers.permissions.add(Permission.objects.get(codename="add_book"))
        manager = CustomUser.objects.create_user("manager", "", "pass12345")
        manager.groups.add(managers)
        CustomUser.objects.create_user("buyer", password="pass12345")

    def test_guest_redirect(self) -> None:
        """Гість."""
        response = self.client.get(reverse("shop:book_create"))
        self.assertRedirects(response, "/users/login/?next=/books/add/")

    def test_buyer_forbidden(self) -> None:
        """Покупець."""
        self.client.login(username="buyer", password="pass12345")
        response = self.client.get(reverse("shop:book_create"))
        self.assertEqual(response.status_code, 403)

    def test_manager_allowed(self) -> None:
        """Менеджер."""
        self.client.login(username="manager", password="pass12345")
        response = self.client.get(reverse("shop:book_create"))
        self.assertEqual(response.status_code, 200)

    def test_register(self) -> None:
        """Реєстрація."""
        response = self.client.post(
            reverse("users:register"),
            {
                "username": "Ihor",
                "email": "Ihor@test.ua",
                "phone": "0501112233",
                "password1": "pass-777",
                "password2": "pass-777",
            },
        )
        self.assertRedirects(response, reverse("shop:book_list"))
        user = CustomUser.objects.get(username="Ihor")
        self.assertTrue(user.groups.filter(name="Покупці").exists())

    def test_logout(self) -> None:
        """Вихід."""
        self.client.login(username="buyer", password="pass12345")
        response = self.client.post(reverse("users:logout"))
        self.assertRedirects(response, reverse("shop:book_list"))
