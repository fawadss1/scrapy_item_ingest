"""
Requests pipeline for tracking request information.
"""
import logging
import time
from datetime import datetime, timezone
from scrapy import signals
from .base import BasePipeline
from ..utils.fingerprint import get_request_fingerprint

logger = logging.getLogger(__name__)


class RequestsPipeline(BasePipeline):
    """Pipeline for handling request tracking"""

    def __init__(self, settings):
        super().__init__(settings)
        self.request_start_times = {}  # Track request start times
        self.request_id_map = {}  # Track fingerprint to database ID mapping
        self.url_to_id_map = {}  # Track URL to database ID mapping
        self.current_response_url = None  # Track current response being processed

    @classmethod
    def from_crawler(cls, crawler):
        """Create pipeline instance from crawler"""
        pipeline = super().from_crawler(crawler)
        # Connect to request signals to automatically log requests
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
                    logger.info(f"Found parent ID {parent_id} from current response URL: {parent_url}")

            # Method 2: Check request meta for referer
            if not parent_id and hasattr(request, 'meta') and request.meta:
                if 'referer' in request.meta:
                    parent_url = request.meta['referer']
                    logger.info(f"Found referer in meta: {parent_url}")

                    # Look up in our URL mapping first (faster)
                    if parent_url in self.url_to_id_map:
                        parent_id = self.url_to_id_map[parent_url]
                        logger.info(f"Found parent ID {parent_id} from URL mapping")
                    else:
                        # Look up in database
                        try:
                            sql = f"SELECT id FROM {self.settings.db_requests_table} WHERE url = %s AND job_id = %s ORDER BY created_at DESC LIMIT 1"
                            result = self.db.execute(sql, (parent_url, job_id))
                            if result:
                                parent_id = result[0]
                                # Cache the result
                                self.url_to_id_map[parent_url] = parent_id
                                logger.info(f"Found parent ID {parent_id} from database lookup")
                        except Exception as e:
                            logger.warning(f"Could not look up parent ID by referer URL: {e}")

                # Debug: Log request meta information
                logger.debug(f"Request URL: {request.url}")
                logger.debug(f"Request meta keys: {list(request.meta.keys()) if request.meta else 'None'}")
                if 'depth' in request.meta:
                    logger.debug(f"Request depth: {request.meta['depth']}")

        except Exception as e:
            logger.warning(f"Could not extract parent request info: {e}")

        # If we still don't have parent info, log for debugging
        if not parent_id and not parent_url:
            logger.debug(f"No parent found for request: {request.url}")

        return parent_id, parent_url

    def log_request(self, request, spider):
        """Log request to database"""
        job_id = self.settings.get_identifier_value(spider)

        logger.info(f"Logging request for job_id {job_id}: {request.url}")
        fingerprint = get_request_fingerprint(request)
        parent_id, parent_url = self._get_parent_request_info(request, spider)
        request_time = time.time()
        created_at = datetime.now(timezone.utc)

        # Store request start time for duration calculation
        self.request_start_times[fingerprint] = request_time

        sql = f"""
        INSERT INTO {self.settings.db_requests_table} 
        (job_id, url, method, fingerprint, parent_id, parent_url, created_at) 
        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
        """
        try:
            result = self.db.execute(sql, (
                job_id,
                request.url,
                request.method,
                fingerprint,
                parent_id,
                parent_url,
                created_at
            ))

            # Get the inserted record ID and store it for future parent lookups
            if result:
                record_id = result[0]
                self.request_id_map[fingerprint] = record_id
                self.url_to_id_map[request.url] = record_id  # Store URL to ID mapping

                self.db.commit()

                log_msg = f"Successfully logged request for job_id {job_id} with fingerprint {fingerprint} (ID: {record_id})"
                if parent_id:
                    log_msg += f" (parent ID: {parent_id}, parent URL: {parent_url})"
                else:
                    log_msg += " (no parent found)"
                logger.info(log_msg)
        except Exception as e:
            logger.error(f"Failed to log request: {e}")
            self.db.rollback()

    def request_scheduled(self, request, spider):
        """Called when a request is scheduled"""
        job_id = self.settings.get_identifier_value(spider)
        logger.info(f"Request scheduled for job_id {job_id}: {request.url}")
        self.log_request(request, spider)

    def response_received(self, response, request, spider):
        """Called when a response is received"""
        job_id = self.settings.get_identifier_value(spider)

        logger.info(f"Response received for job_id {job_id}: {response.url} (status: {response.status})")

        # Set current response URL for parent tracking
        self.current_response_url = response.url

        fingerprint = get_request_fingerprint(request)
        response_time = time.time()

        # Update the request log with response info
        try:
            sql = f"""
            UPDATE {self.settings.db_requests_table} 
            SET status_code = %s, response_time = %s
            WHERE job_id = %s AND fingerprint = %s AND status_code IS NULL
            """
            self.db.execute(sql, (
                response.status,
                response_time,
                job_id,
                fingerprint
            ))
            self.db.commit()
            logger.info(f"Updated request status {response.status} and response_time for fingerprint {fingerprint}")
        except Exception as e:
            logger.error(f"Failed to update request status: {e}")
            self.db.rollback()
