from django.contrib import admin

from store.models import Order, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "price",
        "location",
        "created_at",
    ]
    list_filter = ["location"]
    search_fields = ["title", "description"]
    ordering = ["id"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "receipt_number",
        "user",
        "product_title",
        "unit_price",
        "purchased_at",
    ]
    search_fields = [
        "receipt_number",
        "user__username",
        "product_title",
    ]
    readonly_fields = [
        "receipt_number",
        "purchased_at",
    ]
    list_select_related = ["user", "product"]