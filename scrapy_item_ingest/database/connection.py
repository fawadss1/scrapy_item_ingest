"""
Database connection utilities for scrapy_item_ingest.
"""
import psycopg2
import logging
from urllib.parse import urlparse, unquote

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Database connection manager"""

    def __init__(self, db_url):
        self.db_url = db_url
        self.conn = None
        self.cur = None

    def connect(self):
        """Establish database connection"""
        try:
            result = urlparse(self.db_url)
            user = result.username
            password = unquote(result.password) if result.password else None
            host = result.hostname
            port = result.port
            dbname = result.path.lstrip('/')

            self.conn = psycopg2.connect(
                host=host, port=port, dbname=dbname,
                user=user, password=password
            )
            self.cur = self.conn.cursor()
            logger.info("Database connection established")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False

    def close(self):
        """Close database connection"""
        if hasattr(self, 'cur') and self.cur:
            self.cur.close()
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
        logger.info("Database connection closed")

    def execute(self, sql, params=None):
        """Execute SQL query"""
        try:
            if params:
                self.cur.execute(sql, params)
            else:
                self.cur.execute(sql)
            return self.cur.fetchone() if self.cur.description else None
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            self.conn.rollback()
            raise

    def commit(self):
        """Commit transaction"""
        self.conn.commit()

    def rollback(self):
        """Rollback transaction"""
        self.conn.rollback()
