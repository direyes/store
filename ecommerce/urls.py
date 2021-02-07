from django.conf.urls import url
from django.urls import path
from django.utils.translation import ugettext_lazy as _

from ecommerce.views import ConfirmPaymentView
from ecommerce.views import IndexView
from ecommerce.views import ProductView
from ecommerce.views import PurchaseDetailsView
from ecommerce.views import PurchaseReverseView
from ecommerce.views import PurchaseView
from ecommerce.views import PurchaseListView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    url(_('^product-details/(?P<product_pk>\d+)/$'), ProductView.as_view(), name='product_details'),
    url(_('^new-purchase/$'), PurchaseView.as_view(), name='new_purchase'),
    url(_('^confirm-payment/(?P<purchase_pk>\d+)/$'), ConfirmPaymentView.as_view(), name='confirm_purchase'),
    url(_('^purchases/$'), PurchaseListView.as_view(), name='purchase_list'),
    url(_('^purchase-details/(?P<purchase_pk>\d+)/$'), PurchaseDetailsView.as_view(), name='purchase_details'),
    url(_('^purchase-reverse/(?P<purchase_pk>\d+)/$'), PurchaseReverseView.as_view(), name='purchase_reverse'),
]
