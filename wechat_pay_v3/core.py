# coding=UTF-8
"""
Wechat payments API v3 Core.
"""
from __future__ import absolute_import, unicode_literals

import json
import logging
import requests
import urllib
from .utils import generate_random_string, get_timestamp_string

log = logging.getLogger('django')
WECHAT_PAY_V3_REQUEST_SCHEMA = 'WECHATPAY2-SHA256-RSA2048'
GATE_WAY = 'https://api.mch.weixin.qq.com'


class Core(object):
    _gate_way = GATE_WAY

    def _build_header_auth_token(self, method, relative_url, timestamp, nonce_str, request_body):
        # 2.签名信息
        #
        #     - 发起请求的商户（包括直连商户、服务商或渠道商）的商户号 mchid
        #     - 商户API证书序列号serial_no，用于声明所使用的证书
        #     - 请求随机串nonce_str
        #     - 时间戳timestamp
        #     - 签名值signature
        #
        #     注：以上五项签名信息，无顺序要求。
        signature = self.sign(method, relative_url, timestamp, nonce_str, request_body)
        data = {
            'mchid': self._merchant_id,
            'serial_no': self._serial_number,
            'nonce_str': nonce_str,
            'timestamp': timestamp,
            'signature': signature.decode('UTF-8'),
        }
        token = ','.join(['{}="{}"'.format(k, v) for k, v in data.items()])
        return token

    def _set_request_header(self, method, relative_url, timestamp, nonce_str, request_body):
        # Authorization: <schema> <token>
        # GET - getToken("GET", httpurl, "")
        # POST - getToken("POST", httpurl, json)
        # Authorization: 认证类型 签名信息
        # 1.认证类型，目前为WECHATPAY2-SHA256-RSA2048
        # 2.签名信息
        token = self._build_header_auth_token(method, relative_url, timestamp, nonce_str,
                                              request_body)
        return {
            'Authorization': '{} {}'.format(WECHAT_PAY_V3_REQUEST_SCHEMA, token),
            'User-Agent': 'wechatpay v3 api python sdk',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    def _request_preparation(self, method, relative_url, request_body):
        url = urllib.parse.urljoin(self._gate_way, relative_url)
        timestamp = get_timestamp_string()
        nonce_str = generate_random_string()

        headers = self._set_request_header(method, relative_url, timestamp, nonce_str, request_body)
        # For Debug:
        # headers_string = ' '.join(["--header '{}: {}'".format(k, v) for k, v in headers.items()])
        # print("curl --location --request GET '{}' {}".format(url, headers_string))
        log.info('headers: {}'.format(headers))
        log.info('request_body: {}'.format(request_body))
        return url, headers

    def request_get(self, relative_url):
        url, headers = self._request_preparation('GET', relative_url, '')
        return requests.get(url, headers=headers)

    def request_post(self, relative_url, params):
        request_body = json.dumps(params)
        url, headers = self._request_preparation('POST', relative_url, request_body)
        return requests.post(url, headers=headers, data=request_body)

    def place_a_order(self, description, out_trade_no, time_expire, notify_url,
                      amount_in_cents, openid, attach=None):
        url = '/v3/pay/transactions/jsapi'
        data = {
            'appid': self._app_id,
            'mchid': self._merchant_id,
            'description': description,
            'out_trade_no': out_trade_no,
            'time_expire': time_expire,
            'notify_url': notify_url,
            'amount': {
                'total': int(amount_in_cents),
                'currency': 'CNY',
            },
            "payer": {
                "openid": openid,
            },
            'attach': attach,
        }
        response = self.request_post(url, data)
        log.info('Get response of place_a_order: {}'.format(response.content))
        return response.json()

    def close_order(self):
        pass
