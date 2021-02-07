from django.utils.translation import ugettext_lazy as _


NEW = 'new'
PAID = 'paid'
REVERSED = 'reversed'

PURCHASE_STATUS = (
    (NEW, _('new')),
    (PAID, _('paid')),
    (REVERSED, _('reversed')),
)
