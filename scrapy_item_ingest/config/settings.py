"""
Configuration settings and utilities for scrapy_item_ingest.
"""

# Static table names - no longer configurable
DEFAULT_ITEMS_TABLE = 'job_items'
DEFAULT_REQUESTS_TABLE = 'job_requests'
DEFAULT_LOGS_TABLE = 'job_logs'


class Settings:
    """Settings class to handle configuration options"""

    def __init__(self, crawler_settings):
        self.crawler_settings = crawler_settings

    @property
    def db_url(self):
        return self.crawler_settings.get('DB_URL')

    @property
    def db_type(self):
        return self.crawler_settings.get('DB_TYPE', 'postgres')

    @property
    def db_items_table(self):
        """Return static table name for items"""
        return DEFAULT_ITEMS_TABLE

    @property
    def db_requests_table(self):
        """Return static table name for requests"""
        return DEFAULT_REQUESTS_TABLE

    @property
    def db_logs_table(self):
        """Return static table name for logs"""
        return DEFAULT_LOGS_TABLE

    @property
    def create_tables(self):
        return self.crawler_settings.getbool('CREATE_TABLES', True)

    @property
    def use_job_id(self):
        # JOB_ID only works when CREATE_TABLES = False
        if self.create_tables:
            return False  # Don't use JOB_ID when creating tables
        else:
            return True   # Use JOB_ID when using existing tables

    @property
    def job_id(self):
        # Always return JOB_ID or fallback to None (spider name will be used)
        return self.crawler_settings.get('JOB_ID', None)

    @staticmethod
    def get_identifier_column():
        """Get the identifier column name"""
        return "job_id"

    def get_identifier_value(self, spider):
        """Get the identifier value with smart fallback"""
        job_id = self.crawler_settings.get('JOB_ID', None)

        if self.create_tables:
            # When creating tables, use JOB_ID if provided, else spider name
            return job_id if job_id else spider.name
        else:
            # When using existing tables, use JOB_ID if provided, else spider name
            return job_id if job_id else spider.name


def validate_settings(settings):
    """Validate configuration settings"""
    if not settings.db_url:
        raise ValueError("DB_URL must be set in settings")

    # Job ID is now optional - will use spider name as fallback
    return True
