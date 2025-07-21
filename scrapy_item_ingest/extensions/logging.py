"""
Logging extension for tracking spider events.
"""
import logging
from scrapy import signals
from .base import BaseExtension

logger = logging.getLogger(__name__)


class LoggingExtension(BaseExtension):
    """Extension for logging spider events to database"""

    @classmethod
    def from_crawler(cls, crawler):
        """Create extension instance from crawler"""
        ext = super().from_crawler(crawler)
        # Connect to spider signals
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(ext.spider_error, signal=signals.spider_error)
        crawler.signals.connect(ext.item_dropped, signal=signals.item_dropped)
        return ext

    def spider_opened(self, spider):
        """Called when spider is opened"""
        identifier_column, identifier_value = self.get_identifier_info(spider)
        message = f"{identifier_column.title()} {identifier_value} started"
        self._log_to_database(spider, "SPIDER_OPENED", message)

    def spider_closed(self, spider, reason):
        """Called when spider is closed"""
        identifier_column, identifier_value = self.get_identifier_info(spider)
        message = f"{identifier_column.title()} {identifier_value} closed with reason: {reason}"
        self._log_to_database(spider, "SPIDER_CLOSED", message)

    def spider_error(self, failure, response, spider):
        """Called when spider encounters an error"""
        message = f"Spider error: {str(failure.value)} on {response.url if response else 'unknown URL'}"
        self._log_to_database(spider, "SPIDER_ERROR", message)

    def item_dropped(self, item, response, spider, exception):
        """Called when an item is dropped"""
        message = f"Item dropped: {str(exception)} from {response.url if response else 'unknown URL'}"
        self._log_to_database(spider, "ITEM_DROPPED", message)
