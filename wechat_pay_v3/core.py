# coding=UTF-8
"""
Wechat payments API v3 Core
"""
from __future__ import absolute_import, unicode_literals

import json

import requests
import urllib
from .utils import generate_random_string, get_timestamp_string

# need sign, need private key, merchant_id, serial_number

WECHAT_PAY_V3_REQUEST_SCHEMA = 'WECHATPAY2-SHA256-RSA2048'


class Core(object):
    _client = None
    _gate_way = None

    def __init__(self, client):
        self._client = client
        self._gate_way = 'https://api.mch.weixin.qq.com'

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
        signature = self._client.sign(method, relative_url, timestamp, nonce_str, request_body)
        data = {
            'mchid': self._client._merchant_id,
            'serial_no': self._client._serial_number,
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
        #
        #     - 发起请求的商户（包括直连商户、服务商或渠道商）的商户号 mchid
        #     - 商户API证书序列号serial_no，用于声明所使用的证书
        #     - 请求随机串nonce_str
        #     - 时间戳timestamp
        #     - 签名值signature
        #
        #     注：以上五项签名信息，无顺序要求。
        token = self._build_header_auth_token(method, relative_url, timestamp, nonce_str,
                                              request_body)
        return {
            'Authorization': '{} {}'.format(WECHAT_PAY_V3_REQUEST_SCHEMA, token),
            'User-Agent': 'wechatpay v3 api python sdk',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    def request_get(self, relative_url):
        method = 'GET'
        url = urllib.parse.urljoin(self._gate_way, relative_url)
        timestamp = get_timestamp_string()
        nonce_str = generate_random_string()
        request_body = ''

        headers = self._set_request_header(method, relative_url, timestamp, nonce_str, request_body)
        # For Debug:
        # headers_string = ' '.join(["--header '{}: {}'".format(k, v) for k, v in headers.items()])
        # print("curl --location --request GET '{}' {}".format(url, headers_string))
        response = requests.get(url, headers=headers)
        return response

    def request_post(self, relative_url, params):
        method = 'POST'
        url = urllib.parse.urljoin(self._gate_way, relative_url)
        timestamp = get_timestamp_string()
        nonce_str = generate_random_string()
        request_body = json.dumps(params)

        headers = self._set_request_header(method, relative_url, timestamp, nonce_str, request_body)
        response = requests.post(url, headers=headers, data=params)
        return response

    def place_a_order(self, description, out_trade_no,
                      time_expire, notify_url,
                      amount_in_cents,
                      openid,
                      attach=None,
                      ):
        url = '/v3/pay/transactions/jsapi'
        data = {
            'appid': self._client._app_id,
            'mchid': self._client._merchant_id,
            'description': description,
            'out_trade_no': out_trade_no,
            'time_expire': time_expire,
            'notify_url': notify_url,

            'amount': {
                'total': int(amount_in_cents),
                'currency': 'CNY',
            },
            "payer": {
                # "openid": "oIRH5jo5GYtYSbZ0bMFJhemBIGPo",
                "openid": openid,
            },
            'attach': attach,
        }

        response = self.request_post(url, data)
        print(response)
        return response

    def close_order(self):
        pass
