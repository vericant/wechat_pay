###############
Wechat Payments
###############

Native Wechat Payments.

**Native** here means that Wechat mobile app must be used in order to perform
a payment.

Installation
============

.. code-block:: sh

    pip install git+https://github.com/vericant/wechat_pay.git@0.3.1#egg=wechat_pay

Usage
=====

First of all you need to initialize an object:

.. code-block:: python

    from wechat_pay import WechatPay

    payment = WechatPay('<app id>', '<merchant id>', '<payments key>',
                        '<notify url>', '<server ip>')

Make a prepay request
---------------------

.. code-block:: python

    data = payment.retrieve_prepay_data('<product name>', '<transaction no>',
                                        '<price>')

It will return a dictionary with a bunch of stuff. The part that is
particularly interesting here is **code_url** which looks something like this:
*weixin://wxpay/bizpayurl?pr=e42JWWu*

With this code you could then generate a QR-code image:

.. code-block:: sh

    qrencode -l H -t PNG -o qr.png 'weixin://wxpay/bizpayurl?pr=e42JWWu'

…and show it to your user in order to let her pay.

Full explanation of how this works can be found in service documentation.

Validate notification
---------------------

Right after user makes a payment, Wechat server hits you back to <notify url>
you specified with POST request, body of which contains useful information.
Let's say you got it in the *xml* variable:

.. code-block:: python

    if payment.validate_notification(xml):
        # do something

Close order
-----------

Close the order. For following situations:
  1. The payment is failed, merchant need to generate new order so close the
     original order to avoid duplicated payments.
  2. Over the time, merchant need to close the order.

Note: The min gap time between request order and close the same order is 5
minutes.

.. code-block:: python

    data = payment.close_order('<transaction no>')

It will return a dictionary with a bunch of stuff if closed successfully.

The **'return_code'** in dictionary describe whether it's success/fail.

The **'err_code'** in dictionary describe the error code if it failed.

Full explanation of how this works and error code details can be found in service
documentation.

References
==========

* `Wechat payments (Chinese) <https://pay.weixin.qq.com/wiki/doc/api/index.html>`_
* `JSAPI implementation by @richfisher <https://github.com/richfisher/wechat_pay_py>`_
  which was used originally, and this code still inherits some approaches from.


Hints
=====

Integrations were traditionally hard to test, but not anymore.
Use `localtunnel <https://localtunnel.me>`_ and be happy.
