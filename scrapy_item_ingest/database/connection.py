# scrapy_item_ingest/database/connection.py

import psycopg2
from scrapy.utils.project import get_project_settings


class DBConnection:
    """
    Handles a single persistent PostgreSQL connection for the entire spider runtime.
    Avoids reconnecting for each item, improving performance and reliability.
    """

    _instance = None  # Singleton instance
    _connection = None

    def __new__(cls):
        # Ensure only one instance exists (singleton)
        if cls._instance is None:
            cls._instance = super(DBConnection, cls).__new__(cls)
            cls._instance._initialize_connection()
        return cls._instance

    def _initialize_connection(self):
        """Initialize the PostgreSQL connection once."""
        settings = get_project_settings()
        self._connection = psycopg2.connect(
            host=settings.get("DB_HOST"),
            port=settings.get("DB_PORT"),
            user=settings.get("DB_USER"),
            password=settings.get("DB_PASSWORD"),
            dbname=settings.get("DB_NAME")
        )
        self._connection.autocommit = False  # manual commit per item
        print("✅ Persistent DB connection established once.")

    def get_connection(self):
        """Return the active connection (always the same one)."""
        if self._connection.closed:
            self._initialize_connection()
        return self._connection

    def close(self):
        """Close connection gracefully when the spider ends."""
        if self._connection and not self._connection.closed:
            self._connection.close()
            print("🧹 Database connection closed cleanly.")
