import base64
import json
import pytz
import requests
from datetime import datetime
from datetime import timedelta

from django.conf import settings
from django.db import transaction

from purchase.choices import PAID
from purchase.choices import REVERSED
from purchase.models import Purchase
from purchase.models import PurchaseItem


def get_headers():
    authorization = 'Basic {0}'.format(
        base64.b64encode(
            bytearray(
                '{0}:{1}'.format(
                    settings.TPAGA_USER,
                    settings.TPAGA_USER_PASS,
                ),
                'utf-8',
            ),
        ).decode()
    )
    headers = {
        'Authorization': authorization,
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }

    return headers


@transaction.atomic
def create_purchase(products):
    purchase = Purchase.objects.create()
    items = []
    for item in products:
        items.append(
            PurchaseItem.objects.create(
                quantity=item['quantity'],
                product=item['product'],
                purchase=purchase,
            )
        )
    return request_payment(
        purchase=purchase,
        items=items,
    )


def request_payment(purchase, items):
    """
    curl -X POST \
    https://stag.wallet.tpaga.co/merchants/api/v1/payment_requests/create \
    -H 'Authorization: Basic bWluaWFwcG1hLW1pbmltYWw6YWJjMTIz' \
    -H 'Cache-Control: no-cache' \
    -H 'Content-Type: application/json' \
    -d '{
    "cost":"12000",
    "purchase_details_url":"https://example.com/compra/348820",
    "voucher_url":"https://example.com/comprobante/348820",
    "idempotency_token":"ea0c78c5-e85a-48c4-b7f9-24a9014a2339",
    "order_id":"348820",
    "terminal_id":"sede_45",
    "purchase_description":"Compra en Tienda X",
    "purchase_items":[
        {
            "name":"Aceite de girasol",
            "value":"13.390"
        },
        {
            "name":"Arroz X 80g",
            "value":"4.190"
        }
    ],
    "user_ip_address":"61.1.224.56",
    "expires_at":"2018-11-05T20:10:57.549653+00:00"
    }'
    """

    url = '{0}payment_requests/create'.format(settings.TPAGA_URL)
    timezone = pytz.timezone('America/Bogota')
    purchase_items = []
    cost = 0
    for item in items:
        purchase_items.append(
            {
                'name': item.product.name,
                'value': item.product.value,
            }
        )
        cost += item.product.value * item.quantity
    purchase_data = {
        'cost': cost,
        'purchase_details_url': '{0}confirm-payment/{1}/'.format(
            settings.SITE_URL,
            purchase.pk,
        ),
        'voucher_url': '',
        'idempotency_token': purchase.idempotency_token.__str__(),
        'order_id': purchase.pk,
        'terminal_id': 'sede_45',
        'purchase_description': purchase.get_purchase_description(),
        'purchase_items': purchase_items,
        'user_ip_address': '61.1.224.56',
        'expires_at': (datetime.now() + timedelta(hours=2)).astimezone(timezone).isoformat(),
    }

    response = requests.post(
        url,
        data=json.dumps(purchase_data),
        headers=get_headers(),
    )

    response_data = response.json()
    purchase.payment_token = response_data.get('token')
    purchase.payment_url = response_data.get('tpaga_payment_url')
    purchase.tpaga_status = response_data.get('status')
    purchase.save()
    return purchase


def confirm_purchase(purchase):
    """
    curl -X GET \
    https://stag.wallet.tpaga.co/merchants/api/v1/payment_requests/pr-3d6a2289193bec5adb5080dc2e91cadeba29b58f06ebbba1aba4c9eb85c6777e76811dcd/info \
    -H 'Authorization: Basic bWluaWFwcG1hLW1pbmltYWw6YWJjMTIz' \
    -H 'Cache-Control: no-cache' \
    -H 'Content-Type: application/json'
    """

    url = '{0}payment_requests/{1}/info'.format(
        settings.TPAGA_URL,
        purchase.payment_token,
    )
    response = requests.get(
        url,
        headers=get_headers(),
    )

    response_data = response.json()
    purchase.tpaga_status = response_data.get('status')
    if response_data.get('status') == 'paid':
        purchase.status = PAID
    purchase.save()

    return purchase


@transaction.atomic
def reverse_purchase(purchase):
    """
    curl -X POST \
    https://stag.wallet.tpaga.co/merchants/api/v1/payment_requests/refund \
    -H 'Authorization: Basic bWluaWFwcG1hLW1pbmltYWw6YWJjMTIz' \
    -H 'Cache-Control: no-cache' \
    -H 'Content-Type: application/json' \
    -d '{
    "payment_request_token":"pr-3d6a2289193bec5adb5080dc2e91cadeba29b58f06ebbba1aba4c9eb85c6777e76811dcd"
    }'
    """

    url = '{0}payment_requests/payment_requests/refund'.format(
        settings.TPAGA_URL,
        purchase.payment_token,
    )

    data = {
        'payment_request_token': purchase.payment_token,
    }

    response = requests.post(
        url,
        data=json.dumps(data),
        headers=get_headers(),
    )
    response_data = response.json()
    purchase.tpaga_status = response_data.get('status')
    purchase.status = REVERSED
    purchase.save()

    return purchase
