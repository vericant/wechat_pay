# coding=UTF-8
"""
Wechat payments API v3 Certificate Manager
"""
from __future__ import absolute_import, unicode_literals

import datetime
import logging
import json
import os
from pathlib import Path

from Crypto.PublicKey import RSA
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import Encoding

log = logging.getLogger()


# core.request_get
# sign.aes_decrypt
# _wechat_pay_cert_path 有新的cert，send email to notify tech.
# private_key_path, public_key_path
class CertManager(object):
    _client = None
    _certificates = []
    _wechat_pay_cert_path = None

    def __init__(self, client):
        self._client = client

    def load_certificate_by_bytes(self, pem_bytes):
        try:
            return x509.load_pem_x509_certificate(pem_bytes,
                                                  backend=default_backend())
        except Exception:
            return None

    # ##################### load certificate 平台支付证书
    def load_last_certificate(self, pem_bytes=None):
        """
        openssl x509 -in 1900009191_20180326_cert.pem -noout -serial
        openssl x509 -in wechatpay_14F30EE2534F986F5B572B2D8A873AEC77B438D3.pem \
            -pubkey -noout > wechatpay_14F30EE2534F986F5B572B2D8A873AEC77B438D3_pub.pem

        :return:
        """
        from cryptography import x509

        cert = x509.load_pem_x509_certificate(pem_bytes)
        print(cert.serial_number)
        print('serial number: {0:X}'.format(cert.serial_number))

        # if pem_bytes:
        #     cert = crypto.load_certificate(crypto.FILETYPE_PEM, pem_bytes)
        # else:
        #
        #     # ciphertext = received_message['data'][0]['encrypt_certificate']['ciphertext']
        #     # cert = crypto.load_certificate(crypto.FILETYPE_ASN1, base64.b64decode(ciphertext))
        #     pem_filename = '/Users/doris/Downloads/1235355102_20211124_cert/apiclient_cert.pem'
        #     with open(pem_filename, 'rb') as f:
        #         cert = crypto.load_certificate(crypto.FILETYPE_PEM, f.read())
        # print('serial number: {0:X}'.format(cert.get_serial_number()))
        pass

    def update_certificates(self):
        self._certificates.clear()
        data = self._fetch_all_certificates()

        for value in data:
            serial_no = value.get('serial_no')
            effective_time = value.get('effective_time')
            expire_time = value.get('expire_time')
            encrypt_certificate = value.get('encrypt_certificate')
            algorithm = encrypt_certificate.get('algorithm')
            nonce_str = encrypt_certificate.get('nonce')
            associated_data = encrypt_certificate.get('associated_data')
            ciphertext = encrypt_certificate.get('ciphertext')
            if not (serial_no and effective_time and expire_time and algorithm and
                    nonce_str and associated_data and ciphertext):
                continue

            cert_bytes = self._client.aes_decrypt(ciphertext, nonce_str, associated_data)
            cert = self.load_certificate_by_bytes(cert_bytes)
            if not cert:
                continue

            print('version: ', cert.version)
            print('serial_number: ', cert.serial_number)
            print('not_valid_before: ', cert.not_valid_before)
            print('not_valid_after: ', cert.not_valid_after)
            print('issuer: ', cert.issuer)
            print('subject: ', cert.subject)
            print('signature_hash_algorithm: ', cert.signature_hash_algorithm)
            print('signature_algorithm_oid: ', cert.signature_algorithm_oid)
            print('extensions: ', cert.extensions)
            print('signature: ', cert.signature)
            print('tbs_certificate_bytes: ', cert.tbs_certificate_bytes)

            now = datetime.datetime.utcnow()
            if now < cert.not_valid_before or now > cert.not_valid_after:
                continue
            self._store_certificate(serial_no, cert, cert_bytes)
            self._certificates.append(cert)

    def _fetch_all_certificates(self):
        relative_url = '/v3/certificates'
        response = self._client.request_get(relative_url)
        if response.status_code != 200:
            log.error('get error when fetch all certificates')
            return None
        return json.loads(response.content).get('data')

    def _store_certificate(self, serial_no, cert, cert_bytes):
        Path(self._wechat_pay_cert_path).mkdir(parents=True, exist_ok=True)
        cert_file_name = os.path.join(self._wechat_pay_cert_path,
                                      'wechatpay_{}.pem'.format(serial_no))
        if not os.path.exists(cert_file_name):
            with open(cert_file_name, 'w') as f:
                f.write(cert_bytes.decode())
            public_key_file_name = os.path.join(self._wechat_pay_cert_path,
                                                'wechatpay_{}_pub.pem'.format(serial_no))
            with open(public_key_file_name, 'w') as f:
                f.write(cert.public_bytes(Encoding.PEM).decode())

    def load_private_key(self, private_key_path):
        with open(private_key_path, 'rb') as f:
            return RSA.importKey(f.read())

    def load_public_key(self, public_key_path):
        with open(public_key_path, "rb") as f:
            return RSA.importKey(f.read())
