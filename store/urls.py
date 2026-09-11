from django.urls import path

from store.views import (
    OrderReceiptView,
    ProductDetailView,
    ProductListView,
    PurchaseView,
)


urlpatterns = [
    path(
        "products/",
        ProductListView.as_view(),
        name="product-list",
    ),
    path(
        "products/<int:pk>/",
        ProductDetailView.as_view(),
        name="product-detail",
    ),
    path(
        "orders/",
        PurchaseView.as_view(),
        name="order-create",
    ),
    path(
        "orders/<uuid:receipt_number>/",
        OrderReceiptView.as_view(),
        name="order-receipt",
    ),
]