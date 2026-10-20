import base64
import datetime
import tempfile
from unittest import TestCase
from unittest.mock import Mock, patch

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509.oid import NameOID

from wechat_pay_v3 import (
    WechatPayV3,
    WPV3Decrypt,
    WPV3PreRequest,
    WPV3Verify,
    is_timestamp_fresh,
)
from wechat_pay_v3.core import REQUEST_TIMEOUT
from wechat_pay_v3.keys import load_public_key


class WechatPayV3Test(TestCase):
    _app_id = 'app 1'
    _merchant_id = 'merchant 1'
    _serial_number = None
    _private_key_path = 'tests/test-data/private.pem'
    _public_key_path = 'tests/test-data/public.pem'
    _api_v3_key = '7EVaSd0ZuyXZXy5eJpNb5CuXoEvAzqv3'
    _wechatpay_serial = 'PUB_KEY_ID_0000000000000000000000000000000'


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

    def test_verify_invalid_base64_signature(self):
        wp = WPV3Verify(
            self._merchant_id,
            public_key_path=self._public_key_path,
        )
        for signature in ('abc', 'not base64 at all!', b'abc', ''):
            self.assertFalse(wp.verify('1637893078', 'nonce', 'body', signature))

    def test_keys_are_loaded_once(self):
        wp = WechatPayV3(
            self._merchant_id,
            private_key_path=self._private_key_path,
            public_key_path=self._public_key_path,
        )
        with patch.object(WechatPayV3, 'load_private_key',
                          wraps=wp.load_private_key) as mock_load_private, \
                patch.object(WechatPayV3, 'load_public_key',
                             wraps=wp.load_public_key) as mock_load_public:
            for _ in range(2):
                signature = wp.sign('GET', '/v3/test', '1637893078', 'nonce', '')
                wp.verify('1637893078', 'nonce', 'body', signature)
        self.assertEqual(mock_load_private.call_count, 1)
        self.assertEqual(mock_load_public.call_count, 1)


class WechatPayV3EncryptTest(WechatPayV3Test):
    def test_sensitive_field_encrypt_uses_oaep(self):
        wp = WechatPayV3(
            self._merchant_id,
            public_key_path=self._public_key_path,
        )
        ciphertext = wp.sensitive_field_encrypt('test encryption')

        with open(self._private_key_path, 'rb') as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)
        oaep = padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),
                            algorithm=hashes.SHA1(), label=None)
        self.assertEqual(private_key.decrypt(base64.b64decode(ciphertext), oaep),
                         b'test encryption')

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

    def test_set_request_header_without_wechatpay_serial(self):
        wp = WPV3PreRequest(
            self._merchant_id,
            app_id=self._app_id,
            serial_number=self._serial_number,
            private_key_path=self._private_key_path,
        )
        headers = wp._set_request_header('GET', '/v3/test', '1637893078', 'nonce', '')
        self.assertNotIn('Wechatpay-Serial', headers)

    def test_set_request_header_with_wechatpay_serial(self):
        wp = WPV3PreRequest(
            self._merchant_id,
            app_id=self._app_id,
            serial_number=self._serial_number,
            private_key_path=self._private_key_path,
            wechatpay_serial=self._wechatpay_serial,
        )
        headers = wp._set_request_header('GET', '/v3/test', '1637893078', 'nonce', '')
        self.assertEqual(headers['Wechatpay-Serial'], self._wechatpay_serial)

    @patch('wechat_pay_v3.core.requests.post')
    def test_place_a_order_returns_wechatpay_serial(self, mock_post):
        mock_post.return_value = Mock(
            status_code=200,
            content=b'{"prepay_id": "wx2021"}',
            headers={'Wechatpay-Serial': self._wechatpay_serial, 'Request-ID': 'req-1'},
            json=Mock(return_value={'prepay_id': 'wx2021'}),
        )
        wp = WPV3PreRequest(
            self._merchant_id,
            app_id=self._app_id,
            serial_number=self._serial_number,
            private_key_path=self._private_key_path,
            wechatpay_serial=self._wechatpay_serial,
        )
        result = wp.place_a_order('desc', 'vericant_test_001', '2021-12-11T19:49:41+08:00',
                                  'https://example.com/notify', 1, 'openid 1')
        self.assertEqual(result, {'prepay_id': 'wx2021',
                                  'wechatpay_serial': self._wechatpay_serial})
        self.assertEqual(mock_post.call_args.kwargs['headers']['Wechatpay-Serial'],
                         self._wechatpay_serial)
        self.assertEqual(mock_post.call_args.kwargs['timeout'], REQUEST_TIMEOUT)

    @patch('wechat_pay_v3.core.requests.post')
    def test_request_logs_hide_authorization_and_body(self, mock_post):
        mock_post.return_value = Mock(
            status_code=200, content=b'{}', headers={},
            json=Mock(return_value={}),
        )
        wp = WPV3PreRequest(
            self._merchant_id,
            app_id=self._app_id,
            serial_number=self._serial_number,
            private_key_path=self._private_key_path,
        )
        with self.assertLogs('wechat_pay_v3', level='INFO') as logs:
            wp.place_a_order('desc', 'vericant_test_001', '2021-12-11T19:49:41+08:00',
                             'https://example.com/notify', 1, 'openid secret')
        output = '\n'.join(logs.output)
        self.assertIn('POST /v3/pay/transactions/jsapi', output)
        self.assertNotIn('Authorization', output)
        self.assertNotIn('WECHATPAY2-SHA256-RSA2048', output)
        self.assertNotIn('openid secret', output)


class LoadPublicKeyTest(WechatPayV3Test):
    def test_loads_public_key_from_certificate(self):
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'Tenpay.com sign')])
        now = datetime.datetime.now(datetime.timezone.utc)
        certificate = (
            x509.CertificateBuilder()
            .subject_name(name).issuer_name(name)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now).not_valid_after(now + datetime.timedelta(days=1))
            .sign(private_key, hashes.SHA256())
        )
        with tempfile.NamedTemporaryFile(suffix='.pem') as f:
            f.write(certificate.public_bytes(serialization.Encoding.PEM))
            f.flush()
            public_key = load_public_key(f.name)
        self.assertEqual(public_key.public_numbers(), private_key.public_key().public_numbers())

    def test_loads_spki_public_key(self):
        public_key = load_public_key(self._public_key_path)
        self.assertEqual(public_key.key_size, 2048)


class IsTimestampFreshTest(TestCase):
    def test_is_timestamp_fresh(self):
        now = 1731465272
        self.assertTrue(is_timestamp_fresh(str(now), now=now))
        self.assertTrue(is_timestamp_fresh(str(now - 300), now=now))
        self.assertTrue(is_timestamp_fresh(str(now + 300), now=now))
        self.assertFalse(is_timestamp_fresh(str(now - 301), now=now))
        self.assertFalse(is_timestamp_fresh(str(now), max_age_seconds=10, now=now + 11))

    def test_invalid_timestamp(self):
        for timestamp in ('', None, 'abc'):
            self.assertFalse(is_timestamp_fresh(timestamp))
