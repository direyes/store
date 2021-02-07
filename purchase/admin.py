from django.contrib import admin

from purchase.models import Product
from purchase.models import Purchase
from purchase.models import PurchaseItem


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'value',
    )


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem


class PurchaseAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'status',
        'created_at',
        'expires_at',
        'payment_token',
    )
    inlines = (
        PurchaseItemInline,
    )


admin.site.register(Product, ProductAdmin)
admin.site.register(Purchase, PurchaseAdmin)
