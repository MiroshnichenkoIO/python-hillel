from django.urls import path

from . import views

app_name = "shop"

urlpatterns = [
    path("", views.BookListView.as_view(), name="book_list"),
    path("books/add/", views.BookCreateView.as_view(), name="book_create"),
    path(
        "books/<int:pk>/", views.BookDetailView.as_view(), name="book_detail"
    ),
    path(
        "books/<int:pk>/edit/",
        views.BookUpdateView.as_view(),
        name="book_update",
    ),
    path(
        "books/<int:pk>/delete/",
        views.BookDeleteView.as_view(),
        name="book_delete",
    ),
    path("api/books/", views.book_list_api, name="book_list_api"),
    path(
        "api/books/<int:pk>/", views.book_detail_api, name="book_detail_api"
    ),
    path("api/stats/", views.shop_stats_api, name="shop_stats_api"),
]
