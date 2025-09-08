
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import transaction
from django.utils.text import slugify
from decimal import Decimal
import random

CATEGORIES = [
    "Овочі", "Фрукти", "Мед", "Молочні продукти", "Яйця", "Випічка", "Бакалія", "Напої",
]

PRODUCTS = [
    ("Мед липовий", "Натуральний мед з пасіки. Без домішок.", 240),
    ("Мед гречаний", "Насичений смак і темний колір. Корисний для горла.", 260),
    ("Сир домашній", "Справжній фермерський кисломолочний сир.", 150),
    ("Молоко 3.2%", "Свіже пастеризоване молоко з ферми.", 45),
    ("Яйця курячі, 10 шт", "Домашні яйця у піддоні.", 70),
    ("Хліб житній", "Запашний хліб на заквасці.", 38),
    ("Борошно цільнозернове 1кг", "Мелення на кам’яних жорнах.", 65),
    ("Морква 1кг", "Солодка та соковита морква.", 28),
    ("Буряк 1кг", "Для борщу та салатів.", 24),
    ("Яблука 1кг", "Сорт сезонних яблук, хрусткі та ароматні.", 38),
    ("Груші 1кг", "Соковиті, стиглі.", 55),
    ("Горох колотий 800г", "Високий вміст білка, для супів.", 52),
]

def _set_if_has(instance, field_name, value):
    """Set value to field if it exists on model."""
    if field_name in [f.name for f in instance._meta.get_fields()]:
        setattr(instance, field_name, value)

class Command(BaseCommand):
    help = "Seed Biomarket with demo categories and products (idempotent)."

    @transaction.atomic
    def handle(self, *args, **options):
        # Resolve models dynamically
        try:
            Category = apps.get_model('shop', 'Category')
        except LookupError:
            Category = None
        Product = apps.get_model('shop', 'Product')

        # Build field sets
        product_fields = {f.name: f for f in Product._meta.get_fields()}
        needs_category = 'category' in product_fields
        has_slug = 'slug' in product_fields
        has_price = 'price' in product_fields
        has_stock = 'stock' in product_fields
        has_is_active = 'is_active' in product_fields
        has_currency = 'currency' in product_fields

        # Create categories
        cat_objs = {}
        if Category and needs_category:
            for name in CATEGORIES:
                obj, _ = Category.objects.get_or_create(
                    name=name,
                    defaults={'slug': slugify(name)[:50]} if 'slug' in [f.name for f in Category._meta.get_fields()] else {}
                )
                cat_objs[name] = obj

        # Create products
        created = 0
        for title, desc, uah in PRODUCTS:
            defaults = {}
            if has_price:
                # Assume Decimal price in UAH
                defaults['price'] = Decimal(str(uah))
            if has_stock:
                defaults['stock'] = random.randint(3, 20)
            if has_is_active:
                defaults['is_active'] = True

            obj, is_new = Product.objects.get_or_create(
                name=title if 'name' in product_fields else title[:200],
                defaults=defaults
            )
            if is_new:
                # Optional fields
                _set_if_has(obj, 'description', desc)
                if has_slug and not getattr(obj, 'slug', None):
                    obj.slug = slugify(title)[:50]
                if has_currency and not getattr(obj, 'currency', None):
                    try:
                        from shop.models import Currency
                        uah_curr, _ = Currency.objects.get_or_create(code='UAH', defaults={'name': 'Ukrainian Hryvnia', 'symbol': '₴'})
                        obj.currency = uah_curr
                    except Exception:
                        pass
                if needs_category and cat_objs:
                    # Map by simple heuristic
                    if "мед" in title.lower():
                        obj.category = cat_objs.get("Мед")
                    elif "молоко" in title.lower() or "сир" in title.lower():
                        obj.category = cat_objs.get("Молочні продукти")
                    elif "яйц" in title.lower():
                        obj.category = cat_objs.get("Яйця")
                    elif "борошно" in title.lower() or "хліб" in title.lower():
                        obj.category = cat_objs.get("Випічка")
                    elif "моркв" in title.lower() or "буряк" in title.lower():
                        obj.category = cat_objs.get("Овочі")
                    elif "яблук" in title.lower() or "груш" in title.lower():
                        obj.category = cat_objs.get("Фрукти")
                    else:
                        obj.category = cat_objs.get("Бакалія")
                obj.save()
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Seed complete. Added {created} new products."))
