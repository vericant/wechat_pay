from __future__ import absolute_import, unicode_literals

from unittest import TestCase

from wechat_pay_v3 import (
    WechatPayV3,
    WPV3Decrypt,
    WPV3Verify,
)


class WechatPayV3Test(TestCase):
    _app_id = 'app 1'
    _merchant_id = 'merchant 1'
    _serial_number = None
    _private_key_path = 'tests/test-data/private.pem'
    _public_key_path = 'tests/test-data/public.pem'
    _api_v3_key = '7EVaSd0ZuyXZXy5eJpNb5CuXoEvAzqv3'


class WechatPayV3SignTest(WechatPayV3Test):
    def test_signature(self):
        wp = WechatPayV3(
            self._merchant_id,
            private_key_path=self._private_key_path,
        )

        method = 'GET'
        url = '/v3/certificates'
        timestamp = '1638338995'
        nonce_str = '7YYVKTW3ABVM3YNFQGLJ2OZD1GLASKO1'
        request_body = ''
        expected_signature = (
            b'WhXNsJUz32n5pmvctAAZJL0BdhtE9MNNNzyEqGhYhzKczIkLlvUzQFBxaULRJNu4YOSZVyic3h3r66XI0Xfj4'
            b'pufc94pcoA0umxqfd76BdbO+WBrXZ69OTqF6R1KnVLfIEPc9dFRDjU4PZAbn/gXMxLzsAi7tOsMGSeY4I5Cux'
            b'G0XjFufoHV1gdhIG5a6et+fzeYw9+28e34OoKTMFwgBgE0oVR7ifph6XLDzLS9qv9SUxprk5+KVTSOzg2vF9v'
            b'O93cKBQooK/rjwPYiCRc6rNs6VGP9zCnhlsXkVe361+6b/0ddF6gjsEIjNFmqj1SuvVzshlyeMFrcBlO5o9wT'
            b'hg=='
        )

        result = wp.sign(method, url, timestamp, nonce_str, request_body)
        self.assertEqual(result, expected_signature)

    def test_verify(self):
        wp = WPV3Verify(
            self._merchant_id,
            public_key_path=self._public_key_path,
        )
        timestamp = "1637893078"
        nonce_str = "a0ecabdce1d0cd1ffeff853618922d46"
        response_body = "test for wechatpay v3"
        signature = (b'oL5mSfsRFT2eirulmpVLsQqVhGenOKUvvPMCMM4UHHmjppDPC2SsoX/+enz/jHwsPXZ39rx'
                     b'HxpTKaGTFxao1QAiO3v56AkoHb2cWbzjONhPxR+GD2Dlkb28LicWZ2zsiXbSyRzA19+nuGz'
                     b'djY7IUesvq2SwGb3f241kt9rgCWvdDHj9HlC5RWnF0zuyUoXibNtzg1tulYWG3n/F72AoQh'
                     b'MK+rUI081dYAEhnvQkZ3bvAkEJAmHrzAyTUpbLSqPqDZwnShTP3lTEziQ+ZBMRLFXIhTFVx'
                     b'5JXxPnsy3k3ilgibUlB81IfpV+VqpLsUgbpixpFAc3xWTg5N+w6HY3SULg=='
                     )

        result = wp.verify(timestamp, nonce_str, response_body, signature)
        self.assertTrue(result)


class WechatPayV3EncryptTest(WechatPayV3Test):
    def test_sensitive_field_encrypt_decrypt(self):
        wp = WechatPayV3(
            self._merchant_id,
            public_key_path=self._public_key_path,
        )
        message = 'test encryption'
        result = wp.sensitive_field_encrypt(message)
        self.assertTrue(isinstance(result, bytes))

        wp = WechatPayV3(
            self._merchant_id,
            private_key_path=self._private_key_path,
        )
        decrypted_message = wp.sensitive_field_decrypt(result)
        self.assertEqual(message, decrypted_message)

    def test_aes_decrypt(self):
        wp = WPV3Decrypt(
            self._merchant_id,
            api_v3_key=self._api_v3_key,
        )
        nonce_str = "a0ecabdce1d0cd1ffeff853618922d46"
        data = "test for wechatpay v3 test for wechatpay v3"
        associated_data = 'monkey test'
        cipherbyte = wp._aes_encrypt(data, nonce_str, associated_data)

        decrypted_result = wp.aes_decrypt(cipherbyte, nonce_str, associated_data)
        self.assertEqual(decrypted_result, data.encode())


class WechatPayV3CoreTest(WechatPayV3Test):
    def test_build_header_auth_token(self):
        wp = WechatPayV3(
            self._merchant_id,
            private_key_path=self._private_key_path,
        )
        method = 'GET'
        relative_url = '/v3/test'
        timestamp = "1637893078"
        nonce_str = "a0ecabdce1d0cd1ffeff853618922d46"
        request_body = ''
        signature = wp.sign(method, relative_url, timestamp, nonce_str, request_body)
        token = wp._build_header_auth_token(method, relative_url, timestamp, nonce_str,
                                            request_body)
        self.assertEqual(
            token,
            'mchid="merchant 1",serial_no="None",nonce_str="a0ecabdce1d0cd1ffeff853618922d46",'
            'timestamp="1637893078",signature="{}"'.format(signature.decode()))
