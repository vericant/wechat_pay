# Wechat Payments

WeChat Pay for Vericant:

- `wechat_pay`: APIv2 **Native** payments, where the WeChat mobile app scans a QR code to pay.
- `wechat_pay_v3`: APIv3 **JSAPI** payments, paid inside the WeChat browser.

## Installation

```sh
pip install git+https://github.com/vericant/wechat_pay.git@1.0#egg=wechat_pay
```

## APIv2 Native payments (`wechat_pay`)

First of all you need to initialize an object:

```python
from wechat_pay import WechatPay

payment = WechatPay('<app id>', '<merchant id>', '<payments key>',
                    '<notify url>', '<server ip>')
```

### Make a prepay request

```python
data = payment.retrieve_prepay_data('<product name>', '<transaction no>',
                                    '<price in cents>')
```

It will return a dictionary with a bunch of stuff. The part that is
particularly interesting here is **code_url**, which looks something like this:
`weixin://wxpay/bizpayurl?pr=e42JWWu`

With this code you could then generate a QR-code image:

```sh
qrencode -l H -t PNG -o qr.png 'weixin://wxpay/bizpayurl?pr=e42JWWu'
```

…and show it to your user in order to let her pay.

Full explanation of how this works can be found in the service documentation.

### Validate notification

Right after the user makes a payment, the WeChat server hits you back on the
`<notify url>` you specified with a POST request, the body of which contains
useful information. Let's say you got it in the `xml` variable:

```python
if payment.validate_notification(xml):
    # do something
```

### Close order

Close the order in the following situations:

1. The payment failed, and the merchant needs to generate a new order, so the
   original order is closed to avoid duplicated payments.
2. The order timed out, and the merchant needs to close it.

Note: the minimum gap between placing an order and closing the same order is
5 minutes.

```python
data = payment.close_order('<transaction no>')
```

It will return a dictionary with a bunch of stuff if closed successfully.

- `return_code` describes whether it succeeded or failed.
- `err_code` describes the error code if it failed.

Full explanation of how this works and error code details can be found in the
service documentation.

## APIv3 JSAPI payments (`wechat_pay_v3`)

Each class takes only the keys it needs:

| Class | Used for | Keys |
| --- | --- | --- |
| `WPV3PreRequest` | Place a JSAPI order | merchant API certificate serial, merchant private key `apiclient_key.pem`, optional WeChat Pay public key ID |
| `WPV3PaySign` | Sign the JSAPI pay request for the WeChat browser | merchant private key |
| `WPV3Verify` | Verify a callback signature | WeChat Pay public key, or the platform certificate public key |
| `WPV3Decrypt` | Decrypt a callback resource | APIv3 key |

### Place an order

```python
from wechat_pay_v3 import WPV3PreRequest

wp = WPV3PreRequest(
    '<merchant id>',
    app_id='<app id>',
    serial_number='<merchant API certificate serial>',
    private_key_path='/path/to/apiclient_key.pem',
    wechatpay_serial='PUB_KEY_ID_...',  # optional, WeChat Pay public key ID
)
data = wp.place_a_order(
    description='<product name>',
    out_trade_no='<transaction no>',
    time_expire='2026-11-01T12:00:00+08:00',
    notify_url='<notify url>',
    amount_in_cents=1,
    openid='<payer openid>',
)
prepay_id = data.get('prepay_id')
```

When `wechatpay_serial` is set, the request carries the `Wechatpay-Serial`
header, and WeChat Pay signs the response with its public key instead of the
platform certificate. The returned dict also contains `wechatpay_serial`, the
`Wechatpay-Serial` header of the response, which tells which key signed it.

### Verify and decrypt a callback

The callback's `Wechatpay-Serial` header tells which key signed it:
`PUB_KEY_ID_...` for the WeChat Pay public key, otherwise the platform
certificate serial. Pick the matching public key file:

```python
from wechat_pay_v3 import WPV3Decrypt, WPV3Verify

wp = WPV3Verify('<merchant id>', public_key_path='/path/to/pub_key.pem')
if wp.verify(timestamp, nonce_str, request_body, signature):
    data = WPV3Decrypt('<merchant id>', api_v3_key='<APIv3 key>').aes_decrypt(
        ciphertext, nonce, associated_data)
```

### Switching from the platform certificate to the WeChat Pay public key

See [平台证书切换为微信支付公钥](https://pay.weixin.qq.com/doc/v3/merchant/4012154180.md).

## Tests

```sh
pytest tests/tests.py tests/wechat_pay_v3_tests.py
```

## References

- [WeChat Pay APIv2 (Chinese)](https://pay.weixin.qq.com/wiki/doc/api/index.html)
- [JSAPI implementation by @richfisher](https://github.com/richfisher/wechat_pay_py),
  which was used originally, and this code still inherits some approaches from.

## Hints

Integrations were traditionally hard to test, but not anymore.
Use [localtunnel](https://localtunnel.me) and be happy.
