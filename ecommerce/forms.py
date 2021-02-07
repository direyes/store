from django import forms
from django.utils.translation import ugettext_lazy as _

from ecommerce.business_logic import create_purchase
from purchase.models import Product


class PurchaseProductForm(forms.Form):
    product = forms.ModelChoiceField(
        Product.objects.all(),
        label=_('product'),
    )
    quantity = forms.IntegerField(
        label=_('quantity'),
    )

    def save(self):
        products = [
            {
                'product': self.cleaned_data['product'],
                'quantity': self.cleaned_data['quantity'],
            }
        ]
        create_purchase(products)
