from django.contrib import admin
from .models import Category, Product, ProductImage, Order, OrderItem

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "price", "available", "created"]
    list_filter = ["available", "category"]
    search_fields = ["title", "description"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProductImageInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product", "price", "quantity"]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "full_name", "email", "created", "paid", "total"]
    list_filter = ["paid", "created"]
    search_fields = ["id", "full_name", "email", "phone"]
    readonly_fields = ["created", "payment_provider", "payment_id", "total"]
    inlines = [OrderItemInline]
