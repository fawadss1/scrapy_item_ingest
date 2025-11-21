"""
Request fingerprint utilities for generating unique request identifiers.
"""
import logging

from scrapy.utils.request import fingerprint

logger = logging.getLogger(__name__)


def get_request_fingerprint(request):
    """Generate a fingerprint for the request"""

    fp = fingerprint(request)

    if isinstance(fp, bytes):
        fp = fp.hex()

    fp = fp.replace("\\x", "")

    return fp
