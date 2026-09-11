from rest_framework import serializers

from store.models import Order, Product


class ProductSerializer(serializers.ModelSerializer):

    location_name = serializers.CharField(
        source="get_location_display",
        read_only=True,
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "price",
            "location",
            "location_name",
            "created_at",
        ]
        read_only_fields = fields

class PurchaseSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source="product",
    )


class OrderReceiptSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )
    product_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "receipt_number",
            "username",
            "product_id",
            "product_title",
            "product_location",
            "unit_price",
            "purchased_at",
        ]
        read_only_fields = fields