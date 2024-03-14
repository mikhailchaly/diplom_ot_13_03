from django.db import IntegrityError
from django.db.models import Sum, F, Q
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from ujson import loads as load_json

from .models import Contact, Category, Product, Shop, Order, OrderItem, ProductInfo, Parameter, ProductParameter
from .permissions import IsOwnerOrReadeOnlyOrTypeShop, IsOwnerOrReadeOnlyOrTypeBuyer
from .serializers import ContactSerializer, CategorySerializer, ProductSerializer, ShopSerializer, OrderSerializer, \
    OrderItemSerializer, ProductInfoSerializer, ParameterSerializer, ProductParameterSerializer, \
    ORDERSerializer, ORDERITEMSerializer
from .signals import new_order


class ContactViewSet(ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    permission_classes = [IsAuthenticated]


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    permission_classes = [IsAuthenticated, IsOwnerOrReadeOnlyOrTypeShop]


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    permission_classes = [IsAuthenticated, IsOwnerOrReadeOnlyOrTypeShop]


class ParameterViewSet(ModelViewSet):
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer

    permission_classes = [IsAuthenticated, IsOwnerOrReadeOnlyOrTypeShop]


class ProductParameterViewSet(ModelViewSet):
    queryset = ProductParameter.objects.all()
    serializer_class = ProductParameterSerializer

    permission_classes = [IsAuthenticated, IsOwnerOrReadeOnlyOrTypeShop]


class ShopViewSet(ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer

    permission_classes = [IsAuthenticated, IsOwnerOrReadeOnlyOrTypeShop]

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except:
            pass # сделал так, потому что, если не указывать user(а только token), все ломается,
                 # а так пытается создать магазин, с уже существуещем user, но в базу не записывает...


class ProductInfoViewSet(ModelViewSet):
    queryset = ProductInfo.objects.all()
    serializer_class = ProductInfoSerializer

    permission_classes = [IsAuthenticated, IsOwnerOrReadeOnlyOrTypeShop]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderItemViewSet(ReadOnlyModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = ORDERITEMSerializer

    permission_classes = [IsAuthenticated, IsOwnerOrReadeOnlyOrTypeShop]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderViewSet(ReadOnlyModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    permission_classes = [IsAuthenticated, IsOwnerOrReadeOnlyOrTypeShop]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ORDERviewSet(ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = ORDERSerializer



    permission_classes = [IsAuthenticated, IsOwnerOrReadeOnlyOrTypeBuyer]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        new_order.send(sender=self.__class__, user_id=self.request.user.id) # письмо отправляем в консоль

##################################################################################
class OrderItemView(APIView): # не смог реализовать запросы api, по вашему методу ("items": [ { "external_id": 2, "quantity": 13 } ])
                              # поэтому, сделал хуже, но по свойму...
    def get(self, request, *args, **kwargs):
        basket = Order.objects.filter(user_id=request.user.id, state='basket').prefetch_related(
            'order_items__product_info__product__category',
            "order_items__product_info__product_parameters__parameters"
        ).annotate(total_sum=Sum(F('order_items__quantity')*
                                 F('order_items__product_info__price'))).distinct()

        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data)


    def post(self, request, *args, **kwargs):
        items_sting = request.data.get("items")
        if items_sting:
            try:
                items_dict = load_json(items_sting)
            except ValueError:
                return JsonResponse({"Status": False, 'Errors': "Неверный формат запроса"})
            else:
                # basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
                basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='cart')
                objects_created = 0
                for order_item in items_dict:
                    order_item.update({"order": 'basket'})
                    serializer = OrderItemSerializer(data=order_item)
                    if serializer.is_valid():
                        try:
                            serializer.save()
                        except IntegrityError as error:
                            return JsonResponse({"Status": False, "Errors": str(error)})
                        else:
                            objects_created += 1
                    else:
                        return JsonResponse({"Status": False, "Errors": serializer.errors})

                return JsonResponse({"Status": True, 'Создано объектов': objects_created})
        return JsonResponse({"Status": False, "Errors": "Не указаны все аргументы"})


    def delete(self, request, *args, **kwargs):
        items_sting = request.data.get('items')
        if items_sting:
            items_list = items_sting.split(',')
            basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
            query = Q()
            objects_deleted = False
            for order_item_id in items_list:
                if order_item_id.isdigit():
                    query = query | Q(order_id=basket.id, id=order_item_id)
                    objects_deleted = True

            if objects_deleted:
                deleted_count = Order.objects.filter(query).delete()[0]
                return JsonResponse({"Status": True, "Удалено объектов": deleted_count})
        return JsonResponse({"Status": False, "Errors": "Не указаны все аргументы"})

    def put(self, request, *args, **kwargs):
        items_sting = request.data.get('items')
        if items_sting:
            try:
                items_dict = load_json(items_sting)
            except ValueError:
                return JsonResponse({"Status": False, 'Errors': "Неверный формат запроса"})
            else:
                basket, _ =Order.objects.get_or_create(user_id=request.user.id, state='basket')
                objects_updated = 0
                for order_item in items_dict:
                    if type(order_item['id']) == int and type(order_item['quantity']) == int:
                        objects_updated += OrderItem.objects.filter(order_id=basket.id,
                        id=order_item['id']).update(quantity=order_item['quantity'])
                return JsonResponse({"Status": True, 'Обновлено объектов': objects_updated})
        return JsonResponse({"Status": False, 'Errors': 'Не указаны все аргументы'})

    permission_classes = [IsAuthenticated, IsOwnerOrReadeOnlyOrTypeBuyer]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderView(APIView):

    def get(self, request, *args, **kwargs):
        order = Order.objects.filter(user_id=request.user.id).exclude(state='basket').prefeth_related(
            "order_items__product_info__product__category",
            "order_items__product_info__product_parameters__parameter").select_related('contact').annotate(
            total_sum=Sum(F('order_items__quantity')*F("order_items__product_info__price"))).distinct()

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if {"id", "contact"}.issubset(request.data):
            if request.data['id'].isdigit():
                try:
                    is_updated = Order.objects.filter(
                        user_id=request.user.id, id=request.data['id']).update(
                        contact_id=request.data['contact'],
                        state='new')
                except IntegrityError as error:
                    print(error)
                    return JsonResponse({"Status": False, "Errors": "Неправильно указаны аргументы"})
                else:
                    if is_updated:
                        new_order.send(sender=self.__class__, user_id=request.user.id)
                        return JsonResponse({'Status': True})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    permission_classes = [IsAuthenticated, IsOwnerOrReadeOnlyOrTypeBuyer]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)





