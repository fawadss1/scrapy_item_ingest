"""
Requests pipeline for tracking request information.
"""
import logging

from scrapy import signals

from .base import BasePipeline
from ..utils.fingerprint import get_request_fingerprint
from ..utils.time import get_current_datetime

logger = logging.getLogger(__name__)


class RequestsPipeline(BasePipeline):
    """Pipeline for handling request tracking"""

    def __init__(self, settings):
        super().__init__(settings)
        self.request_id_map = {}  # Track fingerprint to database ID mapping
        self.url_to_id_map = {}  # Track URL to database ID mapping
        self.current_response_url = None  # Track current response being processed
        self.request_start_times = {}  # Track request start times for response_time calculation

    @classmethod
    def from_crawler(cls, crawler):
        """Create pipeline instance from crawler"""
        pipeline = super().from_crawler(crawler)
        # Connect to both signals to track request timing
        crawler.signals.connect(pipeline.request_scheduled, signal=signals.request_scheduled)
        crawler.signals.connect(pipeline.response_received, signal=signals.response_received)
        return pipeline

    def _get_parent_request_info(self, request, spider):
        """Extract parent request information if available"""
        parent_id = None
        parent_url = None

        # Get job_id for the current spider
        job_id = self.settings.get_identifier_value(spider)

        try:
            # Method 1: Use current response URL as parent (most reliable)
            if self.current_response_url and self.current_response_url != request.url:
                parent_url = self.current_response_url
                if parent_url in self.url_to_id_map:
                    parent_id = self.url_to_id_map[parent_url]

            # Method 2: Check request meta for referer
            if not parent_id and hasattr(request, 'meta') and request.meta:
                if 'referer' in request.meta:
                    parent_url = request.meta['referer']

                    # Look up in our URL mapping first (faster)
                    if parent_url in self.url_to_id_map:
                        parent_id = self.url_to_id_map[parent_url]
                    else:
                        # Look up in database
                        try:
                            sql = f"SELECT id FROM {self.settings.db_requests_table} WHERE url = %s AND job_id = %s ORDER BY created_at DESC LIMIT 1"
                            result = self.db.execute(sql, (parent_url, job_id))
                            if result:
                                parent_id = result[0]
                                # Cache the result
                                self.url_to_id_map[parent_url] = parent_id

                        except Exception as e:
                            logger.warning(f"Could not look up parent ID by referer URL: {e}")

        except Exception as e:
            logger.warning(f"Could not extract parent request info: {e}")

        return parent_id, parent_url

    def log_request(self, request, spider, response=None):
        """Log request to database with complete information"""
        job_id = self.settings.get_identifier_value(spider)

        fingerprint = get_request_fingerprint(request)
        parent_id, parent_url = self._get_parent_request_info(request, spider)
        created_at = get_current_datetime(self.settings)

        # Get status code and response time if response is available
        status_code = response.status if response else None
        response_time = None
        
        if response:
            fingerprint = get_request_fingerprint(request)
            request_start_time = self.request_start_times.get(fingerprint)
            if request_start_time:
                current_time = created_at.timestamp()
                response_time = current_time - request_start_time
                # Clean up the start time to free memory
                self.request_start_times.pop(fingerprint, None)

        sql = f"""
        INSERT INTO {self.settings.db_requests_table}
        (job_id, url, method, fingerprint, parent_id, parent_url, status_code, response_time, created_at) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """
        try:
            result = self.db.execute(sql, (
                job_id,
                request.url,
                request.method,
                fingerprint,
                parent_id,
                parent_url,
                status_code,
                response_time,
                created_at
            ))

            # Get the inserted record ID and store it for future parent lookups
            if result:
                record_id = result[0]
                self.request_id_map[fingerprint] = record_id
                self.url_to_id_map[request.url] = record_id  # Store URL to ID mapping

                self.db.commit()

        except Exception as e:
            logger.error(f"Failed to log request: {e}")
            self.db.rollback()

    def request_scheduled(self, request, spider):
        """Called when a request is scheduled - track start time"""
        fingerprint = get_request_fingerprint(request)
        current_time = get_current_datetime(self.settings).timestamp()
        self.request_start_times[fingerprint] = current_time

    def response_received(self, response, request, spider):
        """Called when a response is received - log request with complete info"""

        self.current_response_url = response.url

        # Log the request with complete response information
        self.log_request(request, spider, response)
