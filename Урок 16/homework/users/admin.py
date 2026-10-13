from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Адмінка користувачів."""

    list_display = ("username", "email", "phone", "is_staff")
    fieldsets = UserAdmin.fieldsets + (("Додатково", {"fields": ("phone",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Додатково", {"fields": ("phone",)}),
    )
