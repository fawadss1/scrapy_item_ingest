"""
Database schema management utilities for scrapy_item_ingest.
"""
import logging

logger = logging.getLogger(__name__)


class SchemaManager:
    """Database schema management"""

    def __init__(self, db_connection, settings):
        self.db = db_connection
        self.settings = settings

    def create_items_table(self):
        """Create items table if it doesn't exist"""
        items_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.settings.db_items_table} (
            id SERIAL PRIMARY KEY,
            job_id VARCHAR(255),
            item JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.db.execute(items_table_sql)
        logger.info(f"Items table {self.settings.db_items_table} created/verified with job_id column")

    def create_requests_table(self):
        """Create requests table if it doesn't exist"""
        requests_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.settings.db_requests_table} (
            id SERIAL PRIMARY KEY,
            job_id VARCHAR(255),
            url TEXT,
            method VARCHAR(10),
            status_code INTEGER,
            duration FLOAT,
            response_time FLOAT,
            fingerprint VARCHAR(64),
            parent_id INTEGER,
            parent_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES {self.settings.db_requests_table}(id)
        )
        """
        self.db.execute(requests_table_sql)
        logger.info(f"Requests table {self.settings.db_requests_table} created/verified with job_id column")

    def create_logs_table(self):
        """Create logs table if it doesn't exist"""
        logs_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.settings.db_logs_table} (
            id SERIAL PRIMARY KEY,
            job_id VARCHAR(255),
            level VARCHAR(50),
            message TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.db.execute(logs_table_sql)
        logger.info(f"Logs table {self.settings.db_logs_table} created/verified with job_id column")

    def ensure_tables_exist(self):
        """Create all tables if they don't exist (only if create_tables is True)"""
        if not self.settings.create_tables:
            logger.info("Table creation disabled. Skipping table creation.")
            return

        try:
            self.create_items_table()
            self.create_requests_table()
            self.create_logs_table()
            self.db.commit()
            logger.info("All tables created/verified successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            self.db.rollback()
            raise
