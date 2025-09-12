from django.core.management.base import BaseCommand
from django.utils.text import slugify
from decimal import Decimal
from unidecode import unidecode

class Command(BaseCommand):
    help = "Seed demo categories/products. Use --force to reseed, --if-empty to seed only when empty."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Delete all and reseed")
        parser.add_argument("--if-empty", action="store_true", help="Seed only if there are no products")

    def handle(self, *args, **opts):
        from shop.models import Category, Product, ProductImage
        if opts["if_empty"]:
            if Product.objects.exists():
                self.stdout.write(self.style.WARNING("Products already exist; skipping (--if-empty)."))
                return
        if opts["force"]:
            self.stdout.write("Clearing old data...")
            ProductImage.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()

        data = [
            {
                "category": "Овочі",
                "items": [
                    ("Морква органічна, 1 кг", "Свіжа солодка морква з ферми", "59.00",
                     "https://images.unsplash.com/photo-1542831371-29b0f74f9713"),
                    ("Картопля молода, 2 кг", "Молода картопля для запікання і пюре", "89.00",
                     "https://images.unsplash.com/photo-1518977676601-b53f82aba655"),
                ],
            },
            {
                "category": "Фрукти",
                "items": [
                    ("Яблука Зелені, 1 кг", "Соковиті яблука сорту Гренні Сміт", "75.00",
                     "https://images.unsplash.com/photo-1560807707-8cc77767d783"),
                    ("Банани, 1 кг", "Стиглі банани для перекусів та смузі", "72.00",
                     "https://images.unsplash.com/photo-1571772805064-207c8435df79"),
                ],
            },
            {
                "category": "Молочне",
                "items": [
                    ("Молоко 2.5% — 1 л", "Пастеризоване молоко, 2.5% жирності", "48.00",
                     "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b"),
                    ("Сир твердий 200 г", "Класичний твердий сир для сендвічів", "96.00",
                     "https://images.unsplash.com/photo-1604909052787-44ca1b2b89e5"),
                ],
            },
        ]

        for block in data:
            cat_name = block["category"]
            cat, _ = Category.objects.get_or_create(name=cat_name, defaults={"slug": slugify(unidecode(cat_name))})
            for title, desc, price, img in block["items"]:
                slug = slugify(unidecode(title))
                p, created = Product.objects.get_or_create(
                    slug=slug,
                    defaults={
                        "category": cat,
                        "title": title,
                        "description": desc,
                        "price": Decimal(price),
                        "available": True,
                    },
                )
                if created and img:
                    ProductImage.objects.create(product=p, image_url=img)

        self.stdout.write(self.style.SUCCESS("Seeding complete."))
