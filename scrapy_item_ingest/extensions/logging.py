"""
Logging extension for tracking spider events.
"""
import logging
import threading
from typing import List
from scrapy import signals
from .base import BaseExtension
import time

logger = logging.getLogger(__name__)


class AllowedLoggerFilter(logging.Filter):
    """Filter that first checks an allowlist of logger prefixes, then applies
    optional exclusions by logger prefixes and/or message substrings.
    """
    def __init__(self, allowed_prefixes: List[str], excluded_prefixes: List[str] | None = None, excluded_patterns: List[str] | None = None):
        super().__init__()
        # Normalize and deduplicate
        self._allowed = sorted(set(p for p in allowed_prefixes if p), key=len)
        self._excluded = sorted(set(p for p in (excluded_prefixes or []) if p), key=len)
        self._excluded_patterns = [s for s in (excluded_patterns or []) if s]

    def _is_allowed_logger(self, name: str) -> bool:
        for p in self._allowed:
            if name == p or name.startswith(p + "."):
                return True
        return False

    def _is_excluded_logger(self, name: str) -> bool:
        for p in self._excluded:
            if name == p or name.startswith(p + "."):
                return True
        return False

    def _matches_excluded_pattern(self, message: str) -> bool:
        for pat in self._excluded_patterns:
            try:
                if pat in message:
                    return True
            except Exception:
                # Be safe on any unexpected type issues
                continue
        return False

    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        try:
            name = record.name
            if not self._is_allowed_logger(name):
                return False
            # Exclude by logger name
            if self._is_excluded_logger(name):
                return False
            # Exclude by substring patterns in the formatted message or raw msg
            msg = str(record.getMessage())
            if self._matches_excluded_pattern(msg):
                return False
            return True
        except Exception:
            return False


class DatabaseLogHandler(logging.Handler):
    """Custom logging handler to save all log records to the database in batches,
    with a short TTL-based de-duplication to avoid duplicates due to logger propagation.
    """
    _local = threading.local()
    BATCH_SIZE = 100

    def __init__(self, extension, spider):
        super().__init__()
        self.extension = extension
        self.spider = spider
        self._buffer = []
        # De-duplication cache: fingerprint -> last_seen_ts
        try:
            ttl = extension._get_setting('LOG_DB_DEDUP_TTL', 3)
            self._dedup_ttl = float(ttl) if ttl is not None else 3.0
        except Exception:
            self._dedup_ttl = 3.0
        self._seen = {}
        self._seen_cleanup_counter = 0

    def _fingerprint(self, record: logging.LogRecord, formatted_msg: str):
        # Use logger name, level, and formatted message for stable fingerprint
        return (record.name, record.levelno, formatted_msg)

    def _dedup_allow(self, record: logging.LogRecord, formatted_msg: str) -> bool:
        now = time.time()
        fp = self._fingerprint(record, formatted_msg)
        last = self._seen.get(fp)
        if last is not None and (now - last) < self._dedup_ttl:
            return False
        self._seen[fp] = now
        # Periodically cleanup old entries to keep the cache small
        self._seen_cleanup_counter += 1
        if self._seen_cleanup_counter % 256 == 0:
            cutoff = now - self._dedup_ttl
            try:
                for k, ts in list(self._seen.items()):
                    if ts < cutoff:
                        self._seen.pop(k, None)
            except Exception:
                self._seen.clear()
        return True

    def emit(self, record):
        if getattr(self._local, 'in_emit', False):
            return  # Prevent recursion
        self._local.in_emit = True
        try:
            # Format the log message
            msg = self.format(record)
            if not self._dedup_allow(record, msg):
                return
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
        self._orig_levels = {}  # remember original logger levels to restore

    @classmethod
    def from_crawler(cls, crawler):
        """Create extension instance from crawler"""
        ext = super().from_crawler(crawler)
        # Connect to spider signals
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(ext.spider_error, signal=signals.spider_error)
        crawler.signals.connect(ext.item_dropped, signal=signals.item_dropped)
        # Ensure we flush any late records when the engine stops
        try:
            crawler.signals.connect(ext.engine_stopped, signal=signals.engine_stopped)
        except Exception:
            pass
        return ext

    def _get_setting(self, name, default=None):
        try:
            return self.settings.crawler_settings.get(name, default)
        except Exception:
            return default

    def _parse_logger_list(self, spider_logger_name: str) -> List[str]:
        # Always include spider logger and 'scrapy' namespace
        base_list = {spider_logger_name, 'scrapy'}
        raw = self._get_setting('LOG_DB_LOGGERS', None)
        if raw is None:
            return list(base_list)
        user_list: List[str]
        if isinstance(raw, (list, tuple)):
            user_list = [str(x) for x in raw if x]
        else:
            # Comma-separated string
            user_list = [p.strip() for p in str(raw).split(',') if p.strip()]
        # Merge with base_list to guarantee scrapy + spider are captured
        return list(base_list.union(user_list))

    def _parse_excluded_logger_list(self) -> List[str]:
        """Return excluded logger prefixes. Defaults to filter out scraper noise."""
        raw = self._get_setting('LOG_DB_EXCLUDE_LOGGERS', None)
        default_list = ['scrapy.core.scraper']
        if raw is None:
            return default_list
        if isinstance(raw, (list, tuple)):
            return [str(x) for x in raw if x]
        return [p.strip() for p in str(raw).split(',') if p.strip()]

    def _parse_excluded_patterns(self) -> List[str]:
        """Return excluded substring patterns. Defaults to drop 'Scraped from <' lines."""
        raw = self._get_setting('LOG_DB_EXCLUDE_PATTERNS', None)
        default_list = ['Scraped from <']
        if raw is None:
            return default_list
        if isinstance(raw, (list, tuple)):
            return [str(x) for x in raw if x]
        return [p.strip() for p in str(raw).split(',') if p.strip()]

    def _get_level(self):
        # Default to DEBUG so DB can capture detailed Scrapy lines like "Crawled (200) ..."
        raw = str(self._get_setting('LOG_DB_LEVEL', 'DEBUG')).upper()
        return getattr(logging, raw, logging.DEBUG)

    def _get_capture_level(self):
        """Return the logger capture level used for loggers we attach to.
        This allows capturing more verbose records (e.g., DEBUG) for DB only,
        without impacting console verbosity.
        """
        raw = self._get_setting('LOG_DB_CAPTURE_LEVEL', None)
        if raw is None:
            # Default to the same level as DB store level if no override provided
            return self._get_level()
        try:
            return getattr(logging, str(raw).upper(), self._get_level())
        except Exception:
            return self._get_level()

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

        # Resolve underlying spider logger and limit attachment to top-level loggers
        # to avoid duplicate captures via propagation.
        base_spider_logger = getattr(spider.logger, 'logger', None) or logging.getLogger(spider.name)
        logger_names = [
            base_spider_logger.name,
            'scrapy',
        ]
        self._spider = spider

        # Determine capture level (how much we receive) and store original levels
        capture_level = self._get_capture_level()
        logger_objs = []
        for name in dict.fromkeys(logger_names):  # de-duplicate while preserving order
            try:
                lg = logging.getLogger(name)
                logger_objs.append(lg)
                self._orig_levels[lg] = lg.level
                lg.setLevel(capture_level)
            except Exception:
                pass

        # Build allowed prefixes and handler
        allowed_prefixes = self._parse_logger_list(base_spider_logger.name)
        # Ensure core namespaces are included in filter too
        allowed_prefixes = list(set(allowed_prefixes + [
            'scrapy', 'scrapy.core', 'scrapy.core.engine', 'scrapy.core.scraper', 'scrapy.core.downloader'
        ]))
        handler = DatabaseLogHandler(self, spider)
        handler.setLevel(self._get_level())  # what we store (min level)
        excluded_loggers = self._parse_excluded_logger_list()
        excluded_patterns = self._parse_excluded_patterns()
        handler.addFilter(AllowedLoggerFilter(allowed_prefixes, excluded_loggers, excluded_patterns))
        # Configure batch size if provided
        try:
            batch_size = int(self._get_setting('LOG_DB_BATCH_SIZE', handler.BATCH_SIZE))
            if batch_size > 0:
                handler.BATCH_SIZE = batch_size
        except Exception:
            pass
        # Set formatter to mirror console output
        handler.setFormatter(self._make_formatter())

        # Prevent duplicate attachments
        def already_attached(logger_obj):
            for h in getattr(logger_obj, 'handlers', []):
                if isinstance(h, DatabaseLogHandler) and getattr(h, 'spider', None) is spider and getattr(h, 'extension', None) is self:
                    return True
            return False

        # Attach to spider logger and Scrapy-related loggers
        for lg in logger_objs:
            try:
                if not already_attached(lg):
                    lg.addHandler(handler)
                    self._logger_refs.append(lg)
            except Exception:
                pass

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
        # Restore original logger levels
        try:
            for lg, orig_level in self._orig_levels.items():
                try:
                    lg.setLevel(orig_level)
                except Exception:
                    pass
        finally:
            self._orig_levels = {}
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
