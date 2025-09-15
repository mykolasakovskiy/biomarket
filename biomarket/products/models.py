from typing import Optional

from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="products/", blank=True)
    slug = models.SlugField(unique=True)
    stock = models.PositiveIntegerField(default=0)

    def _generate_unique_slug(self, base_slug: Optional[str] = None) -> str:
        slug = base_slug or slugify(self.name)
        if not slug:
            slug = "product"
        unique_slug = slug
        counter = 1
        queryset = Product.objects.all()
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)
        while queryset.filter(slug=unique_slug).exists():
            unique_slug = f"{slug}-{counter}"
            counter += 1
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        else:
            base_slug = slugify(self.slug) or slugify(self.name)
            self.slug = self._generate_unique_slug(base_slug)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("product_detail", args=[self.slug])
