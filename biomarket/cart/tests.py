from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from products.models import Product

from .models import Cart, CartItem


class AddToCartViewTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Product",
            description="A stock item.",
            price=Decimal("19.99"),
            stock=5,
        )

    def test_add_to_cart_creates_cart_item(self):
        response = self.client.post(reverse("cart:add", args=[self.product.slug]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("cart:home"))

        session = self.client.session
        cart_id = session["cart_id"]
        cart = Cart.objects.get(pk=cart_id)
        cart_item = cart.items.get(product=self.product)

        self.assertEqual(cart_item.quantity, 1)
        self.assertEqual(cart.items.count(), 1)

    def test_add_to_cart_increments_quantity_for_existing_item(self):
        first_response = self.client.post(reverse("cart:add", args=[self.product.slug]))
        self.assertEqual(first_response.status_code, 302)

        second_response = self.client.post(reverse("cart:add", args=[self.product.slug]))
        self.assertEqual(second_response.status_code, 302)
        self.assertEqual(second_response.url, reverse("cart:home"))

        cart_id = self.client.session["cart_id"]
        cart = Cart.objects.get(pk=cart_id)
        cart_item = CartItem.objects.get(cart=cart, product=self.product)

        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart_item.quantity, 2)

    def test_add_to_cart_rejects_get_requests(self):
        response = self.client.get(reverse("cart:add", args=[self.product.slug]))

        self.assertEqual(response.status_code, 405)
        self.assertNotIn("cart_id", self.client.session)
