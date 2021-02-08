from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from ecommerce.business_logic import create_purchase
from purchase.models import Product, Purchase, PurchaseItem


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = (
            'pk',
        )


class NewPurchaseSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()

    def save(self, **kwargs):
        products = [
            {
                'product': Product.objects.get(pk=self.data['product_id']),
                'quantity': self.data['quantity'],
            }
        ]
        return create_purchase(products)

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError(_('Invalid product ID.'))
        return value

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(_('Invalid quantity.'))
        return value


class PurchaseItemSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.product.name

    def get_value(self, obj):
        return obj.product.value

    class Meta:
        model = PurchaseItem
        fields = '__all__'
        read_only_fields = (
            'pk',
        )


class PurchaseSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    def get_items(self, obj):
        return PurchaseItemSerializer(obj.items.through.objects.filter(purchase=obj), many=True).data

    class Meta:
        model = Purchase
        fields = '__all__'
        read_only_fields = (
            'pk',
        )
