from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Product


class ProductModelTests(TestCase):
    def test_slug_auto_generation(self):
        product = Product.objects.create(
            name="Test Product",
            description="A product that should generate a slug automatically.",
            price=Decimal("9.99"),
            stock=10,
        )

        self.assertEqual(product.slug, "test-product")

    def test_slug_auto_generation_uniqueness(self):
        Product.objects.create(
            name="Duplicate Name",
            description="First instance",
            price=Decimal("5.00"),
            stock=5,
        )

        second_product = Product.objects.create(
            name="Duplicate Name",
            description="Second instance",
            price=Decimal("6.00"),
            stock=5,
        )

        self.assertEqual(second_product.slug, "duplicate-name-1")


class ProductListViewTests(TestCase):
    def test_product_list_paginates_results(self):
        for index in range(13):
            Product.objects.create(
                name=f"Product {index}",
                description="Test product",
                price=Decimal("10.00"),
                stock=10,
            )

        response = self.client.get(reverse("product_list"))
        self.assertEqual(response.status_code, 200)

        page_obj = response.context["page_obj"]
        self.assertEqual(page_obj.paginator.count, 13)
        self.assertEqual(page_obj.number, 1)
        self.assertEqual(len(response.context["products"]), 12)

        second_page = self.client.get(reverse("product_list"), {"page": 2})
        self.assertEqual(second_page.status_code, 200)
        second_page_obj = second_page.context["page_obj"]
        self.assertEqual(second_page_obj.number, 2)
        self.assertEqual(len(second_page.context["products"]), 1)

    def test_product_list_filters_by_query(self):
        matching = Product.objects.create(
            name="Organic Honey",
            description="Raw honey from local farms.",
            price=Decimal("12.50"),
            stock=10,
        )
        Product.objects.create(
            name="Fresh Apples",
            description="Crisp and juicy.",
            price=Decimal("3.00"),
            stock=25,
        )
        Product.objects.create(
            name="Bananas",
            description="Ripe and sweet.",
            price=Decimal("2.50"),
            stock=20,
        )

        response = self.client.get(reverse("product_list"), {"q": "honey"})
        self.assertEqual(response.status_code, 200)

        products = list(response.context["products"])
        self.assertEqual(products, [matching])
        self.assertEqual(response.context["q"], "honey")
