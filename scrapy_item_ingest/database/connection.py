# scrapy_item_ingest/database/connection.py

import logging
from typing import Optional, Iterable, Any

import psycopg2
from psycopg2 import OperationalError
from scrapy.utils.project import get_project_settings


class DBConnection:
    """
    PostgreSQL connection manager (singleton) with a small convenience API used by
    pipelines and schema utilities. Supports either a DSN/URL or settings-based
    configuration and exposes `connect/execute/commit/rollback/close` methods.
    """

    _instance = None  # Singleton instance
    _connection = None
    _db_url: Optional[str] = None
    _logger = logging.getLogger(__name__)

    def __new__(cls, db_url: Optional[str] = None):
        # Ensure only one instance exists (singleton) and accept optional db_url
        if cls._instance is None:
            cls._instance = super(DBConnection, cls).__new__(cls)
            if db_url:
                cls._instance._db_url = db_url
            cls._instance._initialize_connection()
        else:
            # If an URL is passed later and we don't have one stored yet, keep it
            if db_url and cls._instance._db_url is None:
                cls._instance._db_url = db_url
                # Do not auto-reconnect here; next use will reconnect if needed
        return cls._instance

    def _initialize_connection(self):
        """Initialize the PostgreSQL connection once (or reconnect if closed)."""
        if self._connection is not None and getattr(self._connection, "closed", 0) == 0:
            return

        source = "unknown"
        try:
            if self._db_url:
                source = "db_url"
                self._connection = psycopg2.connect(self._db_url)
            else:
                settings = get_project_settings()
                source = "Scrapy settings"
                self._connection = psycopg2.connect(
                    host=settings.get("DB_HOST"),
                    port=settings.get("DB_PORT"),
                    user=settings.get("DB_USER"),
                    password=settings.get("DB_PASSWORD"),
                    dbname=settings.get("DB_NAME"),
                )
            self._connection.autocommit = False  # manual commit per item
            self._logger.info(f"✅ Database connection established ({source}).")
        except OperationalError as e:
            # Mask password in logs by not printing full URL; provide hint
            self._logger.error(
                "Failed to connect to database via %s: %s. "
                "Verify DB settings or DSN (host, port, user, dbname).",
                source,
                str(e),
            )
            raise

    # Public API expected by pipelines/schema
    def connect(self) -> bool:
        try:
            self._initialize_connection()
            return True
        except Exception:
            return False

    def cursor(self):
        if self._connection is None or getattr(self._connection, "closed", 1):
            self._initialize_connection()
        return self._connection.cursor()

    def execute(self, sql: str, params: Optional[Iterable[Any]] = None):
        """Execute a SQL statement.
        Returns the first row (tuple) if the statement produces a result set
        (e.g., SELECT or INSERT ... RETURNING), otherwise returns None.
        """
        with self.cursor() as cur:
            if params is not None:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            # If the statement returns rows, fetch one for callers expecting a value
            if cur.description is not None:
                row = cur.fetchone()
                return row
            return None

    def commit(self):
        if self._connection:
            self._connection.commit()

    def rollback(self):
        if self._connection:
            self._connection.rollback()

    def get_connection(self):
        """Return the active connection (always the same one)."""
        if self._connection is None or getattr(self._connection, "closed", 1):
            self._initialize_connection()
        return self._connection

    def close(self):
        """Close connection gracefully when the spider ends."""
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._logger.info("🧹 Database connection closed cleanly.")


# Backwards compatibility: older code imports `DatabaseConnection`
# Export an alias so both names work.
DatabaseConnection = DBConnection
