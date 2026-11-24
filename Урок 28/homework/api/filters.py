import django_filters

from orders.models import Order
from shop.models import Book


class BookFilter(django_filters.FilterSet):
    """Фільтр книг."""

    title = django_filters.CharFilter(
        field_name="title", lookup_expr="icontains"
    )
    author = django_filters.CharFilter(
        field_name="author", lookup_expr="icontains"
    )
    min_price = django_filters.NumberFilter(
        field_name="price", lookup_expr="gte"
    )
    max_price = django_filters.NumberFilter(
        field_name="price", lookup_expr="lte"
    )
    category = django_filters.CharFilter(field_name="category__slug")
    in_stock = django_filters.BooleanFilter(method="filter_in_stock")

    class Meta:
        model = Book
        fields = ["title", "author", "category"]

    def filter_in_stock(self, queryset, name: str, value: bool):
        """Є на складі."""
        if value:
            return queryset.filter(stock__gt=0)
        return queryset.filter(stock=0)


class OrderFilter(django_filters.FilterSet):
    """Фільтр замовлень."""

    created_after = django_filters.DateFilter(
        field_name="created_at", lookup_expr="date__gte"
    )
    created_before = django_filters.DateFilter(
        field_name="created_at", lookup_expr="date__lte"
    )

    class Meta:
        model = Order
        fields = ["paid", "city"]
