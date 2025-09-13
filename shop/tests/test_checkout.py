from decimal import Decimal
from django.test import TestCase, override_settings
from django.conf import settings
from django.http import HttpResponse
from unittest.mock import patch

from shop.models import Category, Product


@override_settings(STRIPE_SECRET_KEY='sk_test', STRIPE_PUBLIC_KEY='pk_test', STRIPE_CURRENCY='usd')
class CheckoutStripeLineItemsTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Cat', slug='cat')
        self.product = Product.objects.create(
            category=self.category,
            title='Test Product',
            slug='test-product',
            description='desc',
            price=Decimal('10.00'),
        )

    def test_line_items_use_product_title(self):
        session = self.client.session
        session[settings.CART_SESSION_ID] = {
            str(self.product.id): {
                'title': self.product.title,
                'price': str(self.product.price),
                'qty': 1,
                'slug': self.product.slug,
            }
        }
        session.save()

        captured = {}

        def fake_create(**kwargs):
            captured['line_items'] = kwargs.get('line_items')
            return type('Obj', (), {'id': 'sess_1', 'url': 'http://example.com/pay'})()

        def fake_redirect(url, **kwargs):
            return HttpResponse()

        post_data = {
            'full_name': 'Test User',
            'email': 'test@example.com',
            'phone': '123456',
            'address': 'Addr',
            'city': 'City',
            'postal_code': '12345',
        }

        with patch('stripe.checkout.Session.create', side_effect=fake_create):
            with patch('shop.views.redirect', side_effect=fake_redirect):
                self.client.post('/checkout/', post_data)

        self.assertEqual(
            captured['line_items'][0]['price_data']['product_data']['name'],
            self.product.title,
        )
