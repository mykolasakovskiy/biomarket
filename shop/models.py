from django.db import models
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True, verbose_name="Назва")
    slug = models.SlugField(max_length=140, unique=True)

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("shop:category", args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, related_name="products", on_delete=models.PROTECT, verbose_name="Категорія")
    title = models.CharField(max_length=200, verbose_name="Назва")
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True, verbose_name="Опис")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")
    available = models.BooleanField(default=True, verbose_name="Доступний")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "Товар"
        verbose_name_plural = "Товари"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("shop:product_detail", args=[self.slug])


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image_url = models.URLField(blank=True, help_text="Повний URL зображення")

    class Meta:
        verbose_name = "Зображення товара"
        verbose_name_plural = "Зображення товарів"

    def __str__(self):
        return f"Image for {self.product.title}"


class Order(models.Model):
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=32)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=120)
    postal_code = models.CharField(max_length=20)
    notes = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    payment_provider = models.CharField(max_length=50, blank=True)
    payment_id = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"

    def __str__(self):
        return f"Order #{self.id} ({'paid' if self.paid else 'unpaid'})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Позиція замовлення"
        verbose_name_plural = "Позиції замовлення"

    def __str__(self):
        return f"{self.product.title} x {self.quantity}"
