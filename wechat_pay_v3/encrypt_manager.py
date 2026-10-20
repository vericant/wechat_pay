# coding=UTF-8
"""
Wechat payments API v3 Encryption Manager.
"""
import base64

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# APIv3 敏感信息加解密 requires RSA/ECB/OAEPWithSHA-1AndMGF1Padding.
OAEP_PADDING = padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),
                            algorithm=hashes.SHA1(), label=None)


class EncryptManager(object):
    def sensitive_field_decrypt(self, cipherbyte):
        if isinstance(cipherbyte, str):
            cipherbyte = cipherbyte.encode()
        decrypted_message = self._private_key.decrypt(base64.b64decode(cipherbyte),
                                                      OAEP_PADDING)
        return decrypted_message.decode()

    def sensitive_field_encrypt(self, message):
        # HTTP头部中应包括RSA公钥加密算法，以声明加密所用的密钥对和证书
        # 证书序列号包含在请求HTTP头部的Wechatpay-Serial
        if isinstance(message, str):
            message = message.encode()
        cipherbyte = self._public_key.encrypt(message, OAEP_PADDING)
        return base64.b64encode(cipherbyte)

    def aes_decrypt(self, cipherbyte, nonce_str, associated_data):
        # 证书和回调报文解密
        aesgcm = AESGCM(self._api_v3_key.encode())
        return aesgcm.decrypt(nonce_str.encode(),
                              base64.b64decode(cipherbyte),
                              associated_data.encode())

    def _aes_encrypt(self, data, nonce_str, associated_data):
        # for testing only now
        aesgcm = AESGCM(self._api_v3_key.encode())
        cipherbyte = aesgcm.encrypt(nonce_str.encode(),
                                    data.encode(),
                                    associated_data.encode())
        return base64.b64encode(cipherbyte)
