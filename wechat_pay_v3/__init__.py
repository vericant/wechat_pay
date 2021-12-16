from __future__ import absolute_import, unicode_literals

from .core import Core
from .sign_manager import SignManager
from .cert_manager import CertManager
from .encrypt_manager import EncryptManager


class WechatPayV3(Core, SignManager, CertManager, EncryptManager):
    _merchant_id = None
    _app_id = None  # place a order, pay
    _serial_number = None  # request header, place a order.
    _private_key_path = None  # sign, request header, sensitive_field_decrypt
    _public_key_path = None  # verify, sensitive_field_encrypt
    _api_v3_key = None  # decrypt received notification data

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

    __private_key = None

    @property
    def _private_key(self):
        return self.__private_key or self.load_private_key(self._private_key_path)

    __public_key = None

    @property
    def _public_key(self):
        return self.__public_key or self.load_public_key(self._public_key_path)


class WPV3PreRequest(WechatPayV3):
    def __init__(self, merchant_id, app_id, serial_number, private_key_path):
        super(WPV3PreRequest, self).__init__(
            merchant_id,
            app_id=app_id,
            serial_number=serial_number,
            private_key_path=private_key_path,
        )


class WPV3PaySign(WechatPayV3):
    def __init__(self, merchant_id, app_id, private_key_path):
        super(WPV3PaySign, self).__init__(
            merchant_id,
            app_id=app_id,
            private_key_path=private_key_path,
        )


class WPV3Verify(WechatPayV3):
    def __init__(self, merchant_id, public_key_path):
        super(WPV3Verify, self).__init__(
            merchant_id,
            public_key_path=public_key_path,
        )


class WPV3Decrypt(WechatPayV3):
    def __init__(self, merchant_id, api_v3_key):
        super(WPV3Decrypt, self).__init__(
            merchant_id,
            api_v3_key=api_v3_key,
        )
