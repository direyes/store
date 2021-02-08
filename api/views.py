from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.serializers import NewPurchaseSerializer
from api.serializers import ProductSerializer
from api.serializers import PurchaseSerializer
from ecommerce.business_logic import confirm_purchase
from ecommerce.business_logic import reverse_purchase
from purchase.models import Product
from purchase.models import Purchase


class ProductViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def list(self, request, *args, **kwargs):
        return super(ProductViewSet, self).list(request, *args, **kwargs)


class PurchaseViewSet(
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer


class NewPurchaseViewSet(mixins.CreateModelMixin, GenericViewSet):
    queryset = Purchase.objects.all()
    serializer_class = NewPurchaseSerializer

    def perform_create(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        purchase = self.perform_create(serializer)
        serializer = PurchaseSerializer(purchase)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ConfirmPurchaseViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        purchase = confirm_purchase(instance)
        serializer = self.get_serializer(purchase)
        return Response(serializer.data)


class ReversePurchaseViewSet(mixins.DestroyModelMixin, GenericViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        purchase = reverse_purchase(instance)
        serializer = self.get_serializer(purchase)
        return Response(serializer.data)
