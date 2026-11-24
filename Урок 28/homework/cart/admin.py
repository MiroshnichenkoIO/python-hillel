from django.contrib import admin

from .models import CartItem, CartModel


class CartItemInline(admin.TabularInline):
    """Рядки кошика."""

    model = CartItem
    raw_id_fields = ("book",)
    extra = 0


@admin.register(CartModel)
class CartModelAdmin(admin.ModelAdmin):
    """Адмінка кошиків."""

    list_display = ("user", "created_at")
    inlines = [CartItemInline]
