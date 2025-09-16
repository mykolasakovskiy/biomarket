from django.conf import settings
from django.db import models


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="carts",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = (
            models.UniqueConstraint(
                fields=("user",),
                name="unique_cart_user",
            ),
        )

    def __str__(self) -> str:
        if self.user:
            return f"Cart #{self.pk} for {self.user}"  # pragma: no cover - string repr only
        return f"Cart #{self.pk}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-added_at",)
        constraints = (
            models.UniqueConstraint(
                fields=("cart", "product"),
                name="unique_cartitem_cart_product",
            ),
        )

    def __str__(self) -> str:
        return f"{self.quantity} x {self.product}"  # pragma: no cover - string repr only
