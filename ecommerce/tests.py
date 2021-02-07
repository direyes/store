import json

from django.conf import settings
from django.test import TestCase
from django.urls import reverse_lazy

import httpretty
from django_dynamic_fixture import G

from purchase.choices import NEW
from purchase.choices import PAID
from purchase.choices import REVERSED
from purchase.models import Product
from purchase.models import Purchase
from purchase.models import PurchaseItem


class PurchaseTest(TestCase):

    def setUp(self):
        self.payment_token = 'pr-39394abaed1d3e97d1fe67423079c36336905671bb5a77877e3b9dc032a3070c52162365'
        self.tpaga_payment_url = 'https://w.tpaga.co/eyJtIjp7Im8iOiJQUiJ9LCJkIjp7InMiOiJtaW5pbWFsLW1hIiwicHJ0IjoicHItMzkzOTRhYmFlZDFkM2U5N2QxZmU2NzQyMzA3OWMzNjMzNjkwNTY3MWJiNWE3Nzg3N2UzYjlkYzAzMmEzMDcwYzUyMTYyMzY1In19'
        self.product = G(
            Product,
            value=100,
        )
        self.purchase = G(
            Purchase,
            payment_token=self.payment_token,
            payment_url=self.tpaga_payment_url,
        )
        self.item = G(
            PurchaseItem,
            quantity=10,
            product=self.product,
            purchase=self.purchase,
        )
        self.new_purchase_url = reverse_lazy('ecommerce:new_purchase')
        self.confirm_purchase_url = reverse_lazy('ecommerce:confirm_purchase', kwargs={'purchase_pk': self.purchase.pk})
        self.reverse_purchase_url = reverse_lazy('ecommerce:purchase_reverse', kwargs={'purchase_pk': self.purchase.pk})

    @httpretty.activate
    def test_new_purchase(self):
        tpaga_status = 'created'
        response_data = {
            'miniapp_user_token': None,
            'cost': '12000.0',
            'purchase_details_url': 'https://example.com/compra/348820',
            'voucher_url': 'https://example.com/comprobante/348820',
            'idempotency_token': 'ea0c78c5-e85a-48c4-b7f9-24a9014a2339',
            'order_id': '348820',
            'terminal_id': 'sede_45',
            'purchase_description': 'Compra en Tienda X',
            'purchase_items': [
                {
                    'name': 'Aceite de girasol',
                    'value': 13390
                },
            ],
            'user_ip_address': '61.1.224.56',
            'merchant_user_id': None,
            'token': self.payment_token,
            'tpaga_payment_url': self.tpaga_payment_url,
            'status': tpaga_status,
            'expires_at': '2018-11-05T15:10:57.549-05:00',
            'cancelled_at': None,
            'checked_by_merchant_at': None,
            'delivery_notification_at': None,
        }
        httpretty.register_uri(
            httpretty.POST,
            '{0}payment_requests/create'.format(settings.TPAGA_URL),
            body=json.dumps(response_data),
            status=200,
            content_type='application/json',
        )
        data = {
            'product': self.product.pk,
            'quantity': 1,
        }
        self.client.post(
            self.new_purchase_url,
            data,
        )

        purchase = Purchase.objects.last()
        self.assertEquals(purchase.payment_token, self.payment_token)
        self.assertEquals(purchase.payment_url, self.tpaga_payment_url)
        self.assertEquals(purchase.tpaga_status, tpaga_status)
        self.assertEquals(purchase.status, NEW)

    @httpretty.activate
    def test_confirm_purchase(self):
        tpaga_status = 'paid'
        response_data = {
            'miniapp_user_token': None,
            'cost': '12000.0',
            'purchase_details_url': 'https://example.com/compra/348820',
            'voucher_url': 'https://example.com/comprobante/348820',
            'idempotency_token': 'ea0c78c5-e85a-48c4-b7f9-24a9014a2339',
            'order_id': '348820',
            'terminal_id': 'sede_45',
            'purchase_description': 'Compra en Tienda X',
            'purchase_items': [
                {
                    'name': 'Aceite de girasol',
                    'value': '13.390'
                },
            ],
            'user_ip_address': '61.1.224.56',
            'merchant_user_id': None,
            'token': self.payment_token,
            'tpaga_payment_url': self.tpaga_payment_url,
            'status': tpaga_status,
            'expires_at': '2018-11-05T15:10:57.549-05:00',
            'cancelled_at': None,
            'checked_by_merchant_at': '2018-10-22T11:26:16.964-05:00',
            'delivery_notification_at': '2018-10-22T11:26:16.980-05:00'
        }
        httpretty.register_uri(
            httpretty.GET,
            '{0}payment_requests/{1}/info'.format(
                settings.TPAGA_URL,
                self.payment_token,
            ),
            body=json.dumps(response_data),
            status=200,
            content_type='application/json',
        )
        self.client.get(
            self.confirm_purchase_url,
        )

        purchase = Purchase.objects.get(pk=self.purchase.pk)
        self.assertEquals(purchase.tpaga_status, tpaga_status)
        self.assertEquals(purchase.status, PAID)

    @httpretty.activate
    def test_reverse_purchase(self):
        tpaga_status = 'reverted'
        response_data = {
            'miniapp_user_token': None,
            'cost': '12000.0',
            'purchase_details_url': 'https://example.com/compra/348820',
            'voucher_url': 'https://example.com/comprobante/348820',
            'idempotency_token': 'ea0c78c5-e85a-48c4-b7f9-24a9014a2339',
            'order_id': '348820',
            'terminal_id': 'sede_45',
            'purchase_description': 'Compra en Tienda X',
            'purchase_items': [
                {
                    'name': 'Aceite de girasol',
                    'value': '13.390'
                },
            ],
            'user_ip_address': '61.1.224.56',
            'merchant_user_id': None,
            'token': self.payment_token,
            'tpaga_payment_url': self.tpaga_payment_url,
            'status': tpaga_status,
            'expires_at': '2018-11-05T15:10:57.549-05:00',
            'cancelled_at': None,
            'checked_by_merchant_at': '2018-10-22T11:26:16.964-05:00',
            'delivery_notification_at': '2018-10-22T11:26:16.980-05:00'
        }
        httpretty.register_uri(
            httpretty.POST,
            '{0}payment_requests/payment_requests/refund'.format(
                settings.TPAGA_URL,
                self.purchase.payment_token,
            ),
            body=json.dumps(response_data),
            status=200,
            content_type='application/json',
        )
        self.client.post(
            self.reverse_purchase_url,
        )

        purchase = Purchase.objects.get(pk=self.purchase.pk)
        self.assertEquals(purchase.tpaga_status, tpaga_status)
        self.assertEquals(purchase.status, REVERSED)
