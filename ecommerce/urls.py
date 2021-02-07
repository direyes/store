from django.conf.urls import url
from django.urls import path
from django.utils.translation import ugettext_lazy as _

from ecommerce.views import ConfirmPaymentView
from ecommerce.views import IndexView
from ecommerce.views import ProductView
from ecommerce.views import PurchaseView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    url(_('^product-details/(?P<product_pk>\d+)/$'), ProductView.as_view(), name='product_details'),
    url(_('^new-purchase/$'), PurchaseView.as_view(), name='new_purchase'),
    url(_('^confirm-payment/(?P<purchase_pk>\d+)/$'), ConfirmPaymentView.as_view(), name='confirm_purchase'),
]
