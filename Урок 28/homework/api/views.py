from django.db import transaction
from django.db.models import Count, QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from cart.models import CartItem, CartModel
from orders.models import Order, OrderItem
from shop.models import Book, Category

from .filters import BookFilter, OrderFilter
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    BookSerializer,
    CartItemSerializer,
    CartSerializer,
    CategoryDetailSerializer,
    CategorySerializer,
    OrderSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    """Категорії."""

    queryset = Category.objects.annotate(books_count=Count("books")).order_by(
        "name"
    )
    serializer_class = CategorySerializer
    lookup_field = "slug"

    def get_permissions(self) -> list:
        """Права."""
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        """Серіалізатор."""
        if self.action == "retrieve":
            return CategoryDetailSerializer
        return CategorySerializer


class BookViewSet(viewsets.ModelViewSet):
    """Книги."""

    queryset = Book.objects.select_related("category").order_by("id")
    serializer_class = BookSerializer
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    filterset_class = BookFilter
    search_fields = ["title", "author", "description"]
    ordering_fields = ["price", "title", "created_at"]

    def get_permissions(self) -> list:
        """Права."""
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAdminUser()]


class CartViewSet(viewsets.ViewSet):
    """Кошик."""

    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def list(self, request: Request) -> Response:
        """Мій кошик."""
        cart, _ = CartModel.objects.get_or_create(user=request.user)
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=["delete"])
    def clear(self, request: Request) -> Response:
        """Очистити."""
        CartItem.objects.filter(cart__user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartItemViewSet(viewsets.ModelViewSet):
    """Рядки кошика."""

    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self) -> QuerySet:
        """Лише свої."""
        if getattr(self, "swagger_fake_view", False):
            return CartItem.objects.none()
        return CartItem.objects.filter(
            cart__user=self.request.user
        ).select_related("book")

    def perform_create(self, serializer) -> None:
        """Свій кошик."""
        cart, _ = CartModel.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Замовлення."""

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = OrderFilter
    ordering_fields = ["created_at"]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self) -> QuerySet:
        """Свої або всі для адміна."""
        orders = Order.objects.prefetch_related("items__book").order_by(
            "-created_at"
        )
        if getattr(self, "swagger_fake_view", False):
            return orders.none()
        if self.request.user.is_staff:
            return orders
        return orders.filter(user=self.request.user)

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Замовлення з кошика."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        items = list(
            CartItem.objects.filter(cart__user=request.user).select_related(
                "book"
            )
        )
        if not items:
            return Response(
                {"error": "Cart is empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            books = Book.objects.select_for_update().in_bulk(
                [item.book_id for item in items]
            )
            for item in items:
                if books[item.book_id].stock < item.quantity:
                    return Response(
                        {"error": f"Not enough stock: {item.book.title}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            order = serializer.save(user=request.user)
            for item in items:
                book = books[item.book_id]
                OrderItem.objects.create(
                    order=order,
                    book=book,
                    price=book.price,
                    quantity=item.quantity,
                )
                book.stock -= item.quantity
                book.save(update_fields=["stock"])
            CartItem.objects.filter(cart__user=request.user).delete()

        return Response(
            self.get_serializer(order).data, status=status.HTTP_201_CREATED
        )

    def update(self, request: Request, *args, **kwargs) -> Response:
        """Лише неоплачене."""
        if self.get_object().paid:
            return Response(
                {"error": "Paid order can not be changed"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """Скасувати."""
        order = self.get_object()
        if order.paid:
            return Response(
                {"error": "Paid order can not be canceled"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        with transaction.atomic():
            for item in order.items.select_related("book"):
                item.book.stock += item.quantity
                item.book.save(update_fields=["stock"])
            order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def mark_paid(self, request: Request, pk: str | None = None) -> Response:
        """Оплачено."""
        order = self.get_object()
        order.paid = True
        order.save(update_fields=["paid"])
        return Response(self.get_serializer(order).data)
