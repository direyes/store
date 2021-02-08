from django.urls import include
from django.urls import path

from rest_framework import routers

from api.views import ProductViewSet
from api.views import PurchaseViewSet

router = routers.DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'purchases', PurchaseViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
