from django.db import models
from django.conf import settings
from decimal import Decimal
from django.core.validators import MinValueValidator


class Category(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
    )
    name = models.CharField(max_length=100)
    monthly_limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name_plural = "categories"
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "name"], name="unique_category_name_per_owner"
            )
        ]

    def __str__(self):
        return self.name
