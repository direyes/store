from django.utils.translation import ugettext_lazy as _


NEW = 'new'
PAID = 'paid'

PURCHASE_STATUS = (
    (NEW, _('new')),
    (PAID, _('paid')),
)
