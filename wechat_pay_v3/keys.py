"""
Wechat payments API v3 RSA key loading.
"""
from cryptography import x509
from cryptography.hazmat.primitives import serialization


def load_private_key(private_key_path):
    """
    商户API证书私钥 apiclient_key.pem, PKCS#8 or PKCS#1.
    """
    with open(private_key_path, 'rb') as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def load_public_key(public_key_path):
    """
    微信支付公钥 pub_key.pem, a platform certificate public key, or a platform certificate.
    """
    with open(public_key_path, 'rb') as f:
        pem_bytes = f.read()
    if b'-----BEGIN CERTIFICATE-----' in pem_bytes:
        return x509.load_pem_x509_certificate(pem_bytes).public_key()
    return serialization.load_pem_public_key(pem_bytes)
