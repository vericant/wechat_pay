"""
Wechat payments API v3 Utils.
"""
import secrets
import string
import time

# WeChat Pay recommends rejecting signatures older than 5 minutes.
SIGNATURE_MAX_AGE_SECONDS = 5 * 60


def generate_random_string(length=32):
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def get_timestamp_string():
    return str(int(time.time()))


def is_timestamp_fresh(timestamp, max_age_seconds=SIGNATURE_MAX_AGE_SECONDS, now=None):
    """
    Whether a Wechatpay-Timestamp header is within max_age_seconds of now, to block replays.
    """
    try:
        timestamp = int(timestamp)
    except (TypeError, ValueError):
        return False
    now = int(time.time()) if now is None else now
    return abs(now - timestamp) <= max_age_seconds
