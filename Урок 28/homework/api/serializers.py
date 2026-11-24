from decimal import Decimal

from rest_framework import serializers

from cart.models import CartItem, CartModel
from orders.models import Order, OrderItem
from shop.models import Book, Category


class CategorySerializer(serializers.ModelSerializer):
    """Категорія."""

    books_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "books_count"]


class BookShortSerializer(serializers.ModelSerializer):
    """Коротко про книгу."""

    class Meta:
        model = Book
        fields = ["id", "title", "author", "price"]


class CategoryDetailSerializer(serializers.ModelSerializer):
    """Категорія з книгами."""

    books = BookShortSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "books"]


class BookSerializer(serializers.ModelSerializer):
    """Книга."""

    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "price",
            "description",
            "stock",
            "category",
            "category_id",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_price(self, value: Decimal) -> Decimal:
        """Ціна."""
        if value <= 0:
            raise serializers.ValidationError("Price must be positive")
        return value


class CartItemSerializer(serializers.ModelSerializer):
    """Рядок кошика."""

    book = BookShortSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(), source="book", write_only=True
    )
    cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source="get_cost"
    )

    class Meta:
        model = CartItem
        fields = ["id", "book", "book_id", "quantity", "cost"]

    def validate_quantity(self, value: int) -> int:
        """Кількість."""
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value

    def validate(self, attrs: dict) -> dict:
        """Залишок."""
        if self.instance is not None:
            attrs.pop("book", None)
        book = attrs.get("book") or self.instance.book
        quantity = attrs.get("quantity", 1)
        if quantity > book.stock:
            raise serializers.ValidationError(
                {"quantity": f"Only {book.stock} in stock"}
            )
        return attrs

    def create(self, validated_data: dict) -> CartItem:
        """Додати або збільшити."""
        item, created = CartItem.objects.get_or_create(
            cart=validated_data["cart"],
            book=validated_data["book"],
            defaults={"quantity": validated_data.get("quantity", 1)},
        )
        if not created:
            item.quantity = min(
                item.quantity + validated_data.get("quantity", 1),
                item.book.stock,
            )
            item.save(update_fields=["quantity"])
        return item


class CartSerializer(serializers.ModelSerializer):
    """Кошик."""

    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        source="get_total_price",
    )

    class Meta:
        model = CartModel
        fields = ["id", "items", "total_price", "created_at"]


class OrderItemSerializer(serializers.ModelSerializer):
    """Рядок замовлення."""

    book = BookShortSerializer(read_only=True)
    cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source="get_cost"
    )

    class Meta:
        model = OrderItem
        fields = ["id", "book", "price", "quantity", "cost"]


class OrderSerializer(serializers.ModelSerializer):
    """Замовлення."""

    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.ReadOnlyField(source="user.username")
    total_cost = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        source="get_total_cost",
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "first_name",
            "last_name",
            "email",
            "city",
            "address",
            "paid",
            "created_at",
            "items",
            "total_cost",
        ]
        read_only_fields = ["id", "paid", "created_at"]
