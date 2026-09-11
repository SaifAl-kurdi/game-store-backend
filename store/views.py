from django.db import transaction
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
)
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from store.models import Order, Product
from store.serializers import (
    OrderReceiptSerializer,
    ProductSerializer,
    PurchaseSerializer,
)


class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="location",
            description="Filter products by JO or SA.",
            required=False,
            type=str,
        ),
    ]
)
class ProductListView(ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = ProductPagination

    def get_queryset(self):
        queryset = Product.objects.all()
        location = self.request.query_params.get("location")

        if location:
            location = location.strip().upper()

            if location not in Product.Location.values:
                raise ValidationError(
                    {
                        "location": (
                            "Location must be either JO or SA."
                        )
                    }
                )

            queryset = queryset.filter(location=location)

        return queryset


class ProductDetailView(RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class PurchaseView(APIView):

    @extend_schema(
        request=PurchaseSerializer,
        responses={201: OrderReceiptSerializer},
    )
    @transaction.atomic
    def post(self, request):
        request_serializer = PurchaseSerializer(
            data=request.data
        )
        request_serializer.is_valid(raise_exception=True)

        product = request_serializer.validated_data["product"]

        order = Order.objects.create(
            user=request.user,
            product=product,
            product_title=product.title,
            product_location=product.location,
            unit_price=product.price,
        )

        response_serializer = OrderReceiptSerializer(order)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

class OrderReceiptView(RetrieveAPIView):
    serializer_class = OrderReceiptSerializer
    lookup_field = "receipt_number"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)