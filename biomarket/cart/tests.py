from decimal import Decimal

from django.contrib.auth import get_user_model
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

    def test_add_to_cart_respects_next_parameter_from_post(self):
        next_url = reverse("products:product_list")
        response = self.client.post(
            reverse("cart:add", args=[self.product.slug]),
            data={"next": next_url},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, next_url)

    def test_add_to_cart_rejects_get_requests(self):
        response = self.client.get(reverse("cart:add", args=[self.product.slug]))
        self.assertEqual(response.status_code, 405)

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

    def test_add_to_cart_does_not_exceed_stock(self):
        self.product.stock = 2
        self.product.save(update_fields=["stock"])

        for _ in range(3):
            response = self.client.post(reverse("cart:add", args=[self.product.slug]))
            self.assertEqual(response.status_code, 302)

        cart_id = self.client.session["cart_id"]
        cart = Cart.objects.get(pk=cart_id)
        cart_item = CartItem.objects.get(cart=cart, product=self.product)

        self.assertEqual(cart_item.quantity, self.product.stock)

    def test_guest_cart_items_persist_after_login(self):
        add_response = self.client.post(reverse("cart:add", args=[self.product.slug]))
        self.assertEqual(add_response.status_code, 302)

        user = get_user_model().objects.create_user(username="jane", password="test-pass")
        self.client.force_login(user)

        response = self.client.get(reverse("cart:home"))
        self.assertEqual(response.status_code, 200)

        user_cart = Cart.objects.get(user=user)
        self.assertEqual(self.client.session["cart_id"], user_cart.pk)
        self.assertEqual(Cart.objects.filter(user=user).count(), 1)

        cart_item = user_cart.items.get(product=self.product)
        self.assertEqual(cart_item.quantity, 1)
        self.assertEqual(user_cart.items.count(), 1)

    def test_cart_items_merge_quantities_on_login(self):
        user = get_user_model().objects.create_user(username="john", password="secret")
        user_cart = Cart.objects.create(user=user)
        CartItem.objects.create(cart=user_cart, product=self.product, quantity=2)

        add_response = self.client.post(reverse("cart:add", args=[self.product.slug]))
        self.assertEqual(add_response.status_code, 302)

        self.client.force_login(user)
        response = self.client.get(reverse("cart:home"))
        self.assertEqual(response.status_code, 200)

        user_cart.refresh_from_db()
        self.assertEqual(self.client.session["cart_id"], user_cart.pk)

        cart_item = user_cart.items.get(product=self.product)
        self.assertEqual(cart_item.quantity, 3)
        self.assertEqual(user_cart.items.count(), 1)
        self.assertEqual(Cart.objects.filter(user=user).count(), 1)
