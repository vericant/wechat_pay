"""
Wechat payments
"""

from __future__ import unicode_literals

import hashlib
import string
import random

import xmltodict
import requests


PAYMENT_URL = 'https://api.mch.weixin.qq.com/pay/unifiedorder'


class WechatPay(object):
    """
    Wechat "native" payments implementation.

    Time diagram: https://pay.weixin.qq.com/wiki/doc/api/native.php?chapter=6_5
    """

    _app_id = None
    _merchant_id = None
    _payments_key = None
    _notify_url = None
    _server_ip = None

    def __init__(self, app_id, merchant_id, payments_key, notify_url,
                 server_ip):
        self._app_id = app_id
        self._merchant_id = merchant_id
        self._payments_key = payments_key
        self._notify_url = notify_url
        self._server_ip = server_ip

    def retrieve_prepay_data(self, product_name, out_trade_no, price):
        """
        Retrieves data you need to create a payment QR-code for a user.
        """

        headers = {'Content-Type': 'application/xml'}
        params = self._prepare_order_params(product_name, out_trade_no, price)
        xml = xmltodict.unparse({'xml': params}).encode('utf-8')

        response = requests.post(PAYMENT_URL, data=xml, headers=headers)
        response.encoding = 'utf-8'
        return decode_xml(response.text)

    def validate_notification(self, xml):
        """
        Notification comes signed in the same manner we're signing our requests.
        """
        params = decode_xml(xml)
        return self._make_a_signature(params) == params.get('sign')

    def _prepare_order_params(self, product_name, out_trade_no, price):
        params = {
            'body': product_name,
            'out_trade_no': out_trade_no,
            'total_fee': price,
            'appid': self._app_id,
            'mch_id': self._merchant_id,
            'notify_url': self._notify_url,
            'spbill_create_ip': self._server_ip,
            'nonce_str': generate_random_string(),
            'trade_type': 'NATIVE',
        }

        params['sign'] = self._make_a_signature(params)

        return params

    def _build_signature_string(self, params):
        """
        Signature string must be build in a very specific way.

        Docs: https://pay.weixin.qq.com/wiki/doc/api/native.php?chapter=4_3
        """

        keys = [k for k in params if k != 'sign' and bool(params[k])]
        keys.sort()

        pieces = ['{}={}'.format(k, params[k]) for k in keys]
        pieces.append('key={}'.format(self._payments_key))

        return '&'.join(pieces)

    def _make_a_signature(self, params):
        """
        Hashed signature string.
        """

        signature_string = self._build_signature_string(params)
        md5_hash = hashlib.md5(signature_string.encode('utf-8'))
        return md5_hash.hexdigest().upper()


def generate_random_string(length=32):
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(random.choice(alphabet) for _ in range(length))


def decode_xml(xml):
    return dict(xmltodict.parse(xml)['xml'])
