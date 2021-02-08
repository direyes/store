from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ecommerce.business_logic import confirm_purchase, reverse_purchase
from purchase.models import Product
from purchase.models import Purchase
from api.serializers import NewPurchaseSerializer
from api.serializers import ProductSerializer
from api.serializers import PurchaseSerializer


class ProductViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def list(self, request, *args, **kwargs):
        return super(ProductViewSet, self).list(request, *args, **kwargs)


class PurchaseViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer

    def perform_create(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        self.serializer_class = NewPurchaseSerializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        purchase = self.perform_create(serializer)
        serializer = PurchaseSerializer(purchase)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        purchase = confirm_purchase(instance)
        serializer = self.get_serializer(purchase)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        super(PurchaseViewSet, self).update()
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        purchase = reverse_purchase(instance)
        serializer = self.get_serializer(purchase)
        return Response(serializer.data)
