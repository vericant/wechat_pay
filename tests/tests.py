from __future__ import unicode_literals
from unittest import TestCase

from wechat_pay import WechatPay, generate_random_string


class WechatPayTest(TestCase):
    _app_id = 'app 1'
    _merchant_id = 'merchant 1'
    _payments_key = 'key 123'
    _notify_url = 'http://localhost/wechat/notify/'
    _server_ip = '127.0.0.1'

    _wp = None

    def setUp(self, *args, **kwargs):
        self._wp = WechatPay(self._app_id, self._merchant_id,
                             self._payments_key, self._notify_url,
                             self._server_ip)

    def test_signature(self):
        params = {
            'a': 'b',
            'c': 'd',
            'ignored_1': '',
            'ignored_2': None,
            'sign': 'also ignored',

        }
        result = self._wp._make_a_signature(params)
        self.assertEqual(result, 'CF51D0C2D9C548E945EAE9EA39A76C52')

    def test_order_xml(self):
        product = 'test product'
        transaction = 'trans_1'
        price = '1'

        params = self._wp._prepare_order_params(product, transaction, price)

        self.assertEqual(params['body'], product)
        self.assertEqual(params['out_trade_no'], transaction)
        self.assertEqual(params['total_fee'], price)
        self.assertEqual(params['appid'], self._app_id)
        self.assertEqual(params['mch_id'], self._merchant_id)
        self.assertEqual(params['notify_url'], self._notify_url)
        self.assertEqual(params['spbill_create_ip'], self._server_ip)
        self.assertEqual(params['trade_type'], 'NATIVE')
        self.assertTrue('nonce_str' in params)
        self.assertTrue('sign' in params)

        signature = self._wp._make_a_signature(params)

        self.assertEqual(params['sign'], signature)

    def test_close_order_params(self):
        trans_no = 'b6def355-5e79-4628-9c1b-89c1e9e90c79'
        params = self._wp._prepare_close_order_params(trans_no)
        self.assertEquals(
            set(params.keys()),
            set(['appid', 'mch_id', 'out_trade_no', 'nonce_str', 'sign'])
        )
        signature = self._wp._make_a_signature(params)
        self.assertEqual(params['sign'], signature)


class RandomStringTest(TestCase):
    def test_generate_random_string(self):
        length = 32
        result = generate_random_string(length)
        self.assertEqual(len(result), length)
