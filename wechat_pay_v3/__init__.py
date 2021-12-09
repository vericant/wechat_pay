from __future__ import absolute_import, unicode_literals

from .core import Core
from .sign_manager import SignManager
from .cert_manager import CertManager
from .encrypt_manager import EncryptManager


class WechatPayV3(object):
    _app_id = None  # place a order, pay
    _merchant_id = None
    _serial_number = None  # request header
    _private_key_path = None  # sign, request header, sensitive_field_decrypt
    _public_key_path = None  # verify, sensitive_field_encrypt
    _api_v3_key = None  # 解密Request得到的证书

    def __init__(self, merchant_id,
                 app_id=None,
                 api_v3_key=None,
                 serial_number=None,
                 private_key_path=None,
                 public_key_path=None,
                 ):
        self._merchant_id = merchant_id
        self._app_id = app_id
        self._serial_number = serial_number
        self._private_key_path = private_key_path
        self._public_key_path = public_key_path
        self._api_v3_key = api_v3_key

    def pay_request(self):
        # Content-Type: application/json
        # Accept: application/json
        pass

    def close_order(self):
        pass

    def sign(self, method, url, timestamp, nonce_str, request_body):
        return self._sign_manager.sign(self._private_key, method, url, timestamp, nonce_str,
                                       request_body)

    def verify(self, timestamp, nonce_str, response_body, signature):
        return self._sign_manager.verify(self._public_key, timestamp, nonce_str, response_body,
                                         signature)

    def aes_decrypt(self, cipherbyte, nonce_str, associated_data):
        return self._encrypt_manager.aes_decrypt(self._api_v3_key,
                                                 cipherbyte, nonce_str, associated_data)

    def sensitive_field_encrypt(self, message):
        return self._encrypt_manager.sensitive_field_encrypt(self._public_key, message)

    def sensitive_field_decrypt(self, message):
        return self._encrypt_manager.sensitive_field_decrypt(self._private_key, message)

    def request_get(self, relative_url):
        return self._core.request_get(relative_url)

    def place_a_order(self, description, out_trade_no,
                      time_expire, notify_url,
                      amount_in_cents,
                      openid,
                      attach=None):
        return self._core.place_a_order(description, out_trade_no,
                                        time_expire, notify_url,
                                        amount_in_cents,
                                        openid,
                                        attach)

    __core = None

    @property
    def _core(self):
        return self.__core or Core(self)

    __sign_manager = None

    @property
    def _sign_manager(self):
        return self.__sign_manager or SignManager()

    __cert_manager = None

    @property
    def _cert_manager(self):
        return self.__cert_manager or CertManager(self)

    __encrypt_manager = None

    @property
    def _encrypt_manager(self):
        return self.__encrypt_manager or EncryptManager(self)

    __private_key = None

    @property
    def _private_key(self):
        return self.__private_key or self._cert_manager.load_private_key(self._private_key_path)

    __public_key = None

    @property
    def _public_key(self):
        return self.__public_key or self._cert_manager.load_public_key(self._public_key_path)
