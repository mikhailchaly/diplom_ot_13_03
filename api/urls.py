from rest_framework.routers import DefaultRouter

from api.views import ContactViewSet, CategoryViewSet, ProductViewSet, ShopViewSet, \
    ProductInfoViewSet, ParameterViewSet, ProductParameterViewSet, OrderItemViewSet, OrderViewSet, ORDERviewSet

router = DefaultRouter()
router.register("contact", ContactViewSet)
router.register("category", CategoryViewSet)
router.register("product", ProductViewSet)
router.register("shop", ShopViewSet)
router.register("productinfo", ProductInfoViewSet)
router.register("parameter", ParameterViewSet)
router.register("productparameter", ProductParameterViewSet)
router.register("order_item_view", OrderItemViewSet)
router.register("order_view", OrderViewSet)
router.register("my_order", ORDERviewSet)


urlpatterns = router.urls