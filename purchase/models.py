from django.db import models
from django.utils.translation import ugettext_lazy as _

from uuid import uuid4

from purchase.choices import NEW
from purchase.choices import PURCHASE_STATUS


class Product(models.Model):
    name = models.CharField(
        max_length=140,
        verbose_name=_('name'),
    )
    value = models.PositiveIntegerField(
        verbose_name=_('value'),
    )
    image = models.FileField(
        verbose_name=_('image'),
    )

    def __str__(self):
        return '{0} - ${1}'.format(
            self.name,
            self.value,
        )

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')


class Purchase(models.Model):
    status = models.CharField(
        max_length=140,
        choices=PURCHASE_STATUS,
        default=NEW,
        verbose_name=_('status'),
    )
    idempotency_token = models.UUIDField(
        default=uuid4,
        editable=False,
        verbose_name=_('idempotency token'),
    )
    items = models.ManyToManyField(
        'purchase.Product',
        through='purchase.PurchaseItem',
        verbose_name=_('items'),
    )
    payment_token = models.CharField(
        max_length=140,
        null=True,
        blank=True,
        verbose_name=_('payment token'),
    )
    payment_url = models.CharField(
        max_length=240,
        null=True,
        blank=True,
        verbose_name=_('payment url'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created_at'),
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('expires_at'),
    )

    def get_purchase_description(self):
        return _('Purchase #{0}').format(self.id)

    def __str__(self):
        return '{0}'.format(self.id)

    def get_total_value(self):
        return sum([item.product.value * item.quantity for item in self.items.through.objects.filter(purchase=self)])

    class Meta:
        verbose_name = _('purchase')
        verbose_name_plural = _('purchases')


class PurchaseItem(models.Model):
    quantity = models.PositiveIntegerField(
        verbose_name=_('quantity'),
    )
    product = models.ForeignKey(
        'purchase.Product',
        on_delete=models.PROTECT,
        verbose_name=_('product'),
    )
    purchase = models.ForeignKey(
        'purchase.Purchase',
        on_delete=models.PROTECT,
        verbose_name=_('purchase'),
    )

    class Meta:
        verbose_name = _('purchase item')
        verbose_name_plural = _('purchase items')
