from django.contrib import admin

from .models import Book, Category


class BookInline(admin.TabularInline):
    """Книги всередині категорії."""

    model = Book
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Адмінка категорій."""

    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [BookInline]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Адмінка книг."""

    list_display = ("title", "author", "category", "price", "stock")
    list_filter = ("category",)
    search_fields = ("title", "author")
