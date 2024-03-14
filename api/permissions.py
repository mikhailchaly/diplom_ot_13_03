from rest_framework.permissions import (BasePermission, SAFE_METHODS)


class IsOwnerOrReadeOnlyOrTypeShop(BasePermission): # Для менеджеров магазинов
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated and
            request.user.type == 'shop'
        )

    def has_object_permission(self, request, view, obj):
        if request.user == obj.user:
            return True


class IsOwnerOrReadeOnlyOrTypeBuyer(BasePermission): # Для покупателей
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated and
            request.user.type == 'buyer'
        )

    def has_object_permission(self, request, view, obj):
        if request.user == obj.user:
            return True


