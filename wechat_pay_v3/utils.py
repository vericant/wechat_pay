"""
Wechat payments API v3 Utils.
"""
from __future__ import absolute_import, unicode_literals

import random
import string
import time


def generate_random_string(length=32):
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(random.choice(alphabet) for _ in range(length))


def get_timestamp_string():
    return str(time.time()).split('.')[0]
