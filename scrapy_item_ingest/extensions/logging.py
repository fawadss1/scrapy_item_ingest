"""
Logging extension for tracking spider events.
"""
import logging
import threading
from typing import List
from scrapy import signals
from .base import BaseExtension

logger = logging.getLogger(__name__)


class AllowedLoggerFilter(logging.Filter):
    """Allow records whose logger name starts with any of the allowed prefixes."""
    def __init__(self, allowed_prefixes: List[str]):
        super().__init__()
        # Normalize and deduplicate
        self._allowed = sorted(set(p for p in allowed_prefixes if p), key=len)

    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        try:
            name = record.name
            for p in self._allowed:
                if name == p or name.startswith(p + "."):
                    return True
            return False
        except Exception:
            return False


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
        self._logger_refs = []  # list of loggers we attached to

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

    def _get_setting(self, name, default=None):
        try:
            return self.settings.crawler_settings.get(name, default)
        except Exception:
            return default

    def _parse_logger_list(self, spider_logger_name: str) -> List[str]:
        # Default: spider logger + 'scrapy'
        default_list = [spider_logger_name, 'scrapy']
        raw = self._get_setting('LOG_DB_LOGGERS', None)
        if raw is None:
            return default_list
        if isinstance(raw, (list, tuple)):
            return [str(x) for x in raw if x]
        # Comma-separated string
        return [p.strip() for p in str(raw).split(',') if p.strip()]

    def _get_level(self):
        raw = str(self._get_setting('LOG_DB_LEVEL', 'INFO')).upper()
        return getattr(logging, raw, logging.INFO)

    def _make_formatter(self):
        fmt = self._get_setting('LOG_FORMAT', '%(asctime)s [%(name)s] %(levelname)s: %(message)s')
        datefmt = self._get_setting('LOG_DATEFORMAT', '%Y-%m-%d %H:%M:%S')
        try:
            return logging.Formatter(fmt=fmt, datefmt=datefmt)
        except Exception:
            return logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s')

    def spider_opened(self, spider):
        """Called when spider is opened"""
        identifier_column, identifier_value = self.get_identifier_info(spider)
        message = f"{identifier_column.title()} {identifier_value} started"

        # Resolve underlying spider logger and Scrapy framework logger
        base_spider_logger = getattr(spider.logger, 'logger', None) or logging.getLogger(spider.name)
        scrapy_logger = logging.getLogger('scrapy')
        self._spider = spider

        # Build allowed prefixes and handler
        allowed_prefixes = self._parse_logger_list(base_spider_logger.name)
        handler = DatabaseLogHandler(self, spider)
        handler.setLevel(self._get_level())
        handler.addFilter(AllowedLoggerFilter(allowed_prefixes))
        # Configure batch size if provided
        try:
            batch_size = int(self._get_setting('LOG_DB_BATCH_SIZE', handler.BATCH_SIZE))
            if batch_size > 0:
                handler.BATCH_SIZE = batch_size
        except Exception:
            pass
        # Set formatter to mirror console output
        handler.setFormatter(self._make_formatter())

        # Prevent duplicate attachments: check both loggers
        def already_attached(logger_obj):
            for h in getattr(logger_obj, 'handlers', []):
                if isinstance(h, DatabaseLogHandler) and getattr(h, 'spider', None) is spider and getattr(h, 'extension', None) is self:
                    return True
            return False

        # Attach to spider logger
        if not already_attached(base_spider_logger):
            base_spider_logger.addHandler(handler)
            self._logger_refs.append(base_spider_logger)
        # Also attach to Scrapy framework logger
        if not already_attached(scrapy_logger):
            scrapy_logger.addHandler(handler)
            self._logger_refs.append(scrapy_logger)

        # Keep reference so we can flush/remove later
        self._db_log_handler = handler

        # Emit start message through spider.logger so it's captured
        spider.logger.info(message)

    def spider_closed(self, spider, reason):
        """Called when spider is closed"""
        identifier_column, identifier_value = self.get_identifier_info(spider)
        message = f"{identifier_column.title()} {identifier_value} closed with reason: {reason}"
        # Emit close message via spider logger
        spider.logger.info(message)
        # Flush and detach from all loggers we attached to
        if self._db_log_handler:
            try:
                self._db_log_handler.flush()
            except Exception:
                pass
        for lg in self._logger_refs:
            try:
                if self._db_log_handler:
                    lg.removeHandler(self._db_log_handler)
            except Exception:
                pass
        # Clear references
        self._db_log_handler = None
        self._spider = None
        self._logger_refs = []

    def spider_error(self, failure, response, spider):
        """Called when spider encounters an error"""
        message = f"Spider error: {str(failure.value)} on {response.url if response else 'unknown URL'}"
        self._log_to_database(spider, "ERROR", message)

    def item_dropped(self, item, response, spider, exception):
        """Called when an item is dropped"""
        message = f"Item dropped: {str(exception)} from {response.url if response else 'unknown URL'}"
        self._log_to_database(spider, "INFO", message)
