from django.urls import include
from django.urls import path

from rest_framework import routers

from api.views import ConfirmPurchaseViewSet
from api.views import NewPurchaseViewSet
from api.views import ProductViewSet
from api.views import ReversePurchaseViewSet

from api.views import PurchaseViewSet

router = routers.DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'purchases', PurchaseViewSet)
router.register(r'new-purchase', NewPurchaseViewSet)
router.register(r'confirm-purchase', ConfirmPurchaseViewSet)
router.register(r'reverse-purchase', ReversePurchaseViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
