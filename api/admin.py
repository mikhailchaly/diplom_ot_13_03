from django.contrib import admin

from api.models import Contact, Category, Product, Shop, ProductInfo, Parameter, ProductParameter, Order, OrderItem
from api.serializers import ORDERSerializer


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ["city", 'street', 'house', 'structure', 'apartment', 'phone']
    list_filter = ['city']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["id", 'name', 'category']
    list_filter = ['id']


class ProductInfoInlines(admin.TabularInline):
    model = ProductInfo
    extra = 2


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name', 'url', 'state']
    list_filter = ['name']
    inlines = [ProductInfoInlines]


@admin.register(Parameter)
class ParametrAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_filter = ['name']


@admin.register(ProductParameter)
class ProductParameter(admin.ModelAdmin):
    list_display = ['parameter', 'value']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 3


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    _total_summa = ORDERSerializer.total_summa # !!! Выдает queryset. Сделать, чтоб выдавал чистый итог суммы не смог...

    list_display = ['id', "user", 'state', 'address', 'created_at', "_total_summa"]
    inlines = [OrderItemInline]
