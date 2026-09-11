import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Product(models.Model):

    class Location(models.TextChoices):
        JORDAN = "JO", "Jordan"
        SAUDI_ARABIA = "SA", "Saudi Arabia"

    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    location = models.CharField(
        max_length=2,
        choices=Location.choices,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(location__in=["JO", "SA"]),
                name="product_valid_location",
            )
        ]

    def __str__(self):
        return self.title


class Order(models.Model):

    receipt_number = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="orders",
    )

    # Product information saved at the time of purchase
    product_title = models.CharField(max_length=255)
    product_location = models.CharField(max_length=2)
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-purchased_at"]

    def __str__(self):
        return str(self.receipt_number)