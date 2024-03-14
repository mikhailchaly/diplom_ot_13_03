from django.db.models import F, Sum
from rest_framework import serializers

from .models import Contact, Category, Product, ProductInfo, Shop, OrderItem, Order, ProductParameter, Parameter


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ["id", 'city', 'street', "house", 'structure', 'apartment', 'phone']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", 'name']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', "name", "category"]


class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ['id', 'name']


class ProductParameterSerializer(serializers.ModelSerializer):
    #parameter = serializers.StringRelatedField()

    class Meta:
        model = ProductParameter
        fields = ["id", 'parameter', 'value']


class ProductInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductInfo
        fields = ["id", "product", 'external_id', 'quantity', 'price', 'product_parameters']


class ShopSerializer(serializers.ModelSerializer):
    positions = ProductInfoSerializer(many=True)

    class Meta:
        model = Shop
        fields = ['id', 'user', 'name', 'url', 'address', 'state', "positions"]

    def create(self, validated_data):
        positions = validated_data.pop('positions')
        shop = super().create(validated_data)

        for position in positions:
            ProductInfo.objects.create(shop=shop, **position)
        return shop

    def update(self, instance, validated_data):
        positions = validated_data.pop('positions')
        shop = super().update(instance, validated_data)

        for position in positions:
            ProductInfo.objects.update_or_create(
                shop=shop,
                external_id=position.get("external_id"),
                product=position.get("product"),
                default={
                    "quantity": position.get("quantity"),
                    "product_parameters": position.get("product_parameters")
                }
            )


class ORDERITEMSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', "product_info", 'quantity']


class ORDERSerializer(serializers.ModelSerializer):
    order_items = ORDERITEMSerializer(many=True)
    _total_summa = serializers.SerializerMethodField("total_summa", read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'state', 'address', 'order_items', '_total_summa']

    def total_summa(self, obj):
        return obj.order_items.annotate(per_item_price=F('product_info_id__price') * F('quantity')).annotate(
            total_summa=Sum('per_item_price')).values('total_summa')

    def create(self, validated_data):
        order_items = validated_data.pop('order_items')
        order = super().create(validated_data)

        for position in order_items:
            OrderItem.objects.create(order=order, **position)
        return order

    def update(self, instance, validated_data):
        order_items = validated_data.pop('order_items')
        order = super().update(instance, validated_data)

        for position in order_items:
            OrderItem.objects.update_or_create(
                oder=order,
                default={
                    'product_info': position.get('product_info'), # !!! Работает по id product_info
                    'quantity': position.get('quantity')          # Добраться до external_id, увы не смог
                })
        return order


###############################################################################


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product_info', 'quantity', 'order']
        read_only_fields = ('id',)
        extra_kwargs = {
            'order': {'write_only': True}
        }


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'state', 'address', 'order_items', 'total_price']
        read_only_fields = ("id",)


