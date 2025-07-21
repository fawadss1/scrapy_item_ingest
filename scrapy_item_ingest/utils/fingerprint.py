"""
Request fingerprint utilities for generating unique request identifiers.
"""
import hashlib
import logging

logger = logging.getLogger(__name__)


def get_request_fingerprint(request):
    """Generate fingerprint for the request"""
    try:
        from scrapy.utils.request import request_fingerprint
        return request_fingerprint(request)
    except Exception as e:
        logger.warning(f"Could not generate fingerprint: {e}")
        # Fallback fingerprint generation
        fingerprint_data = f"{request.method}:{request.url}"
        return hashlib.sha1(fingerprint_data.encode()).hexdigest()


def generate_url_fingerprint(method, url):
    """Generate a simple fingerprint for URL and method combination"""
    fingerprint_data = f"{method}:{url}"
    return hashlib.sha1(fingerprint_data.encode()).hexdigest()
