# coding=UTF-8
"""
Wechat payments API v3 Signature Manager.
"""
from __future__ import absolute_import, unicode_literals

import base64
import logging

from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256

log = logging.getLogger('django')


class SignManager(object):
    def sign(self, method, url, timestamp, nonce_str, request_body):
        """
        Hashed signature string.
        计算签名值
        """
        message_string = self._sign_build_message_string(method, url, timestamp, nonce_str,
                                                         request_body)
        signer = PKCS1_v1_5.new(self._private_key)
        signature = signer.sign(SHA256.new(message_string.encode('UTF-8')))
        return base64.b64encode(signature)

    def _sign_build_message_string(self, method, url, timestamp, nonce_str, request_body):
        """
        :param method: http request method, e.g. GET, POST, PUT.
        :param url: API absolute url, e.g. "/v3/certificates" or "/v3/certificate?"
        :param timestamp: the time in seconds since the epoch.
        :param nonce_str: random string, 32 chars.
        :param request_body:
        :return: signature string

        Docs: https://pay.weixin.qq.com/wiki/doc/apiv3/wechatpay/wechatpay4_0.shtml
        构造签名串
        签名串一共有五行，每一行为一个参数。行尾以 \n（换行符，ASCII编码值为0x0A）结束，包括最后一行。
        如果参数本身以\n结束，也需要附加一个\n。

           HTTP请求方法\n
           URL\n
           请求时间戳\n
           请求随机串\n
           请求报文主体\n
        """
        return '\n'.join([method, url, timestamp, nonce_str, request_body, ''])

    # ##################### Verify
    def verify(self, timestamp, nonce_str, response_body, signature):
        message = self._verify_build_message_string(timestamp, nonce_str, response_body)
        hash_value = SHA256.new(message.encode())
        verifier = PKCS1_v1_5.new(self._public_key)
        if isinstance(signature, str):
            signature = signature.encode()
        return verifier.verify(hash_value, base64.decodebytes(signature))

    def _verify_build_message_string(self, timestamp, nonce_str, response_body):
        return '\n'.join([timestamp, nonce_str, response_body, ''])

    def pay_sign(self, timestamp, nonce_str, package):
        """
        Hashed signature string.
        计算签名值
        """
        message_string = self._pay_sign_build_message_string(self._app_id,
                                                             timestamp, nonce_str, package)
        signer = PKCS1_v1_5.new(self._private_key)
        signature = signer.sign(SHA256.new(message_string.encode('UTF-8')))
        return base64.b64encode(signature)

    def _pay_sign_build_message_string(self, app_id, timestamp, nonce_str, package):
        """
        Docs: https://pay.weixin.qq.com/wiki/doc/apiv3/apis/chapter3_1_4.shtml
        构造签名串
        签名串一共有四行，每一行为一个参数。行尾以\n（换行符，ASCII编码值为0x0A）结束，包括最后一行。
        如果参数本身以\n结束，也需要附加一个\n

            应用ID\n
            时间戳\n
            随机字符串\n
            订单详情扩展字符串\n
        """
        return '\n'.join([app_id, timestamp, nonce_str, package, ''])
