"""
Logging extension for tracking spider events.
"""
import logging
import threading
from scrapy import signals
from .base import BaseExtension

logger = logging.getLogger(__name__)


class DatabaseLogHandler(logging.Handler):
    """Custom logging handler to save all log records to the database in batches."""
    _local = threading.local()
    BATCH_SIZE = 100

    def __init__(self, extension, spider):
        super().__init__()
        self.extension = extension
        self.spider = spider
        self._buffer = []

    def emit(self, record):
        if getattr(self._local, 'in_emit', False):
            return  # Prevent recursion
        self._local.in_emit = True
        try:
            # Format the log message
            msg = self.format(record)
            level = record.levelname
            self._buffer.append((self.spider, level, msg))
            if len(self._buffer) >= self.BATCH_SIZE:
                self.flush()
        except Exception:
            # Avoid infinite recursion if logging fails
            pass
        finally:
            self._local.in_emit = False

    def flush(self):
        if not self._buffer:
            return
        try:
            for spider, level, msg in self._buffer:
                self.extension._log_to_database(spider, level, msg)
        except Exception:
            pass
        finally:
            self._buffer.clear()


class LoggingExtension(BaseExtension):
    """Extension for logging spider events to database"""

    def __init__(self, settings):
        super().__init__(settings)
        self._db_log_handler = None
        self._spider = None

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
        self._log_to_database(spider, "INFO", message)
        # Attach custom DB log handler to root logger
        self._spider = spider
        self._db_log_handler = DatabaseLogHandler(self, spider)
        self._db_log_handler.setLevel(logging.DEBUG)
        logging.getLogger().addHandler(self._db_log_handler)

    def spider_closed(self, spider, reason):
        """Called when spider is closed"""
        identifier_column, identifier_value = self.get_identifier_info(spider)
        message = f"{identifier_column.title()} {identifier_value} closed with reason: {reason}"
        self._log_to_database(spider, "INFO", message)
        # Remove the DB log handler
        if self._db_log_handler:
            self._db_log_handler.flush()  # Flush any remaining logs
            logging.getLogger().removeHandler(self._db_log_handler)
            self._db_log_handler = None
            self._spider = None

    def spider_error(self, failure, response, spider):
        """Called when spider encounters an error"""
        message = f"Spider error: {str(failure.value)} on {response.url if response else 'unknown URL'}"
        self._log_to_database(spider, "ERROR", message)

    def item_dropped(self, item, response, spider, exception):
        """Called when an item is dropped"""
        message = f"Item dropped: {str(exception)} from {response.url if response else 'unknown URL'}"
        self._log_to_database(spider, "INFO", message)
