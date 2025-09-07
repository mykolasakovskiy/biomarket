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
        return reverse('shop:category', args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.PROTECT, verbose_name="Категорія")
    title = models.CharField(max_length=200, verbose_name="Назва")
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True, verbose_name="Опис")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")
    stock = models.PositiveIntegerField(default=0, verbose_name="Залишок")
    is_active = models.BooleanField(default=True, verbose_name="Активний")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        verbose_name = "Товар"
        verbose_name_plural = "Товари"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('shop:product', args=[self.slug])


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image_url = models.URLField(max_length=500, verbose_name="URL зображення")

    class Meta:
        verbose_name = "Зображення товару"
        verbose_name_plural = "Зображення товарів"

    def __str__(self):
        return f"Зображення для {self.product.title}"


class Order(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False, verbose_name="Оплачено")
    payment_provider = models.CharField(max_length=30, blank=True, verbose_name="Провайдер оплати")
    payment_id = models.CharField(max_length=120, blank=True, verbose_name="ID платежу")

    full_name = models.CharField(max_length=120, verbose_name="ПІБ")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=32, verbose_name="Телефон")
    address = models.CharField(max_length=255, verbose_name="Адреса")
    city = models.CharField(max_length=120, verbose_name="Місто")
    postal_code = models.CharField(max_length=20, verbose_name="Поштовий індекс")
    notes = models.TextField(blank=True, verbose_name="Коментар")

    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сума замовлення")

    class Meta:
        ordering = ['-created']
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"

    def __str__(self):
        return f"Order #{self.id}"


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
