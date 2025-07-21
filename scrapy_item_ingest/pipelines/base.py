"""
Base pipeline functionality for scrapy_item_ingest.
"""
import logging
from scrapy import signals
from ..config.settings import Settings, validate_settings
from ..database.connection import DatabaseConnection
from ..database.schema import SchemaManager

logger = logging.getLogger(__name__)


class BasePipeline:
    """Base pipeline with common functionality"""

    def __init__(self, settings):
        self.settings = settings
        self.db = None
        self.schema_manager = None
        validate_settings(settings)

    @classmethod
    def from_crawler(cls, crawler):
        """Create pipeline instance from crawler"""
        settings = Settings(crawler.settings)
        return cls(settings)

    def open_spider(self, spider):
        """Called when spider is opened"""
        # Establish database connection
        self.db = DatabaseConnection(self.settings.db_url)
        if not self.db.connect():
            raise Exception("Failed to connect to database")

        # Initialize schema manager
        self.schema_manager = SchemaManager(self.db, self.settings)

        # Ensure tables exist
        self.schema_manager.ensure_tables_exist()

        logger.info(f"Pipeline opened for {self.settings.get_identifier_column()}: {self.settings.get_identifier_value(spider)}")

    def close_spider(self, spider):
        """Called when spider is closed"""
        if self.db:
            self.db.close()
        logger.info(f"Pipeline closed for {self.settings.get_identifier_column()}: {self.settings.get_identifier_value(spider)}")

    def get_identifier_info(self, spider):
        """Get identifier column and value for the spider"""
        return self.settings.get_identifier_column(), self.settings.get_identifier_value(spider)
