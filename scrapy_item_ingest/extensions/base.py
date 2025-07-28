"""
Base extension functionality for scrapy_item_ingest.
"""
import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from ..config.settings import validate_settings
from scrapy_item_ingest.config.settings import Settings
import pytz

logger = logging.getLogger(__name__)


class BaseExtension:
    """Base extension with common functionality"""

    def __init__(self, settings):
        self.settings = settings
        validate_settings(settings)

    @classmethod
    def from_crawler(cls, crawler):
        """Create extension instance from crawler"""
        settings = Settings(crawler.settings)
        return cls(settings)

    def get_identifier_info(self, spider):
        """Get identifier column and value for the spider"""
        return self.settings.get_identifier_column(), self.settings.get_identifier_value(spider)

    def _ensure_logs_table_exists(self, engine):
        """Create logs table if it doesn't exist (only if create_tables is True)"""
        if not self.settings.create_tables:
            logger.info("Table creation disabled. Skipping logs table creation.")
            return

        try:
            with engine.connect() as connection:
                # Determine the identifier column name
                identifier_column = self.settings.get_identifier_column()

                # Create logs table with type, message, and timestamp
                logs_table_sql = f"""
                CREATE TABLE IF NOT EXISTS {self.settings.db_logs_table} (
                    id SERIAL PRIMARY KEY,
                    {identifier_column} VARCHAR(255),
                    type VARCHAR(50),
                    message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
                connection.execute(text(logs_table_sql))
                connection.commit()
                logger.info(f"Logs table {self.settings.db_logs_table} created/verified with {identifier_column} column")
        except Exception as e:
            logger.error(f"Failed to create logs table: {e}")

    def _log_to_database(self, spider, log_level, message):
        """Helper method to log messages to database"""
        try:
            identifier_column, identifier_value = self.get_identifier_info(spider)

            engine = create_engine(self.settings.db_url)
            self._ensure_logs_table_exists(engine)

            stmt = text(f"""
                INSERT INTO {self.settings.db_logs_table}
                ({identifier_column}, level, message, timestamp) 
                VALUES (:identifier, :type, :message, :timestamp)
            """)
            with engine.connect() as connection:
                tz = pytz.timezone(self.settings.get_tz())
                connection.execute(stmt, {
                    "identifier": identifier_value,
                    "type": log_level,
                    "message": message,
                    "timestamp": datetime.now(tz)
                })
                connection.commit()
                logger.info(f"Logged {log_level} for {identifier_column} {identifier_value}")
        except Exception as e:
            logger.error(f"Failed to log {log_level}: {e}")
