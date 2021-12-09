# coding=UTF-8
"""
Wechat payments API v3 Encryption Manager
"""
from __future__ import absolute_import, unicode_literals

import base64

from Crypto.Cipher import PKCS1_v1_5
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# private key, public key, api_v3_key
class EncryptManager(object):
    _client = None

    def __init__(self, client):
        self._client = client

    # ##################### decrypt received response

    # 敏感信息加解密
    def sensitive_field_decrypt(self, private_key, cipherbyte):
        if isinstance(cipherbyte, str):
            cipherbyte = cipherbyte.encode()
        cipher = PKCS1_v1_5.new(private_key)
        decrypted_message = cipher.decrypt(base64.b64decode(cipherbyte), '')
        return decrypted_message.decode()

    def sensitive_field_encrypt(self, public_key, message):
        # HTTP头部中应包括RSA公钥加密算法，以声明加密所用的密钥对和证书
        # 证书序列号包含在请求HTTP头部的Wechatpay-Serial
        if isinstance(message, str):
            message = message.encode()
        encrypter = PKCS1_v1_5.new(public_key)
        cipherbyte = encrypter.encrypt(message)
        return base64.b64encode(cipherbyte)

    def aes_decrypt(self, api_v3_key, cipherbyte, nonce_str, associated_data):
        # 证书和回调报文解密
        aesgcm = AESGCM(api_v3_key.encode())
        return aesgcm.decrypt(nonce_str.encode(),
                              base64.b64decode(cipherbyte),
                              associated_data.encode())

    def _aes_encrypt(self, api_v3_key, data, nonce_str, associated_data):
        # for testing only now
        aesgcm = AESGCM(api_v3_key.encode())
        cipherbyte = aesgcm.encrypt(nonce_str.encode(),
                                    data.encode(),
                                    associated_data.encode())
        return base64.b64encode(cipherbyte)
