
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from api.views import OrderItemView, OrderView

urlpatterns = [

    path("admin/", admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    path('users/', include('new_user.urls')),
    path("api/v1/", include("api.urls")),
    path("basket/", OrderItemView.as_view()),
    path("order/", OrderView.as_view())


]
