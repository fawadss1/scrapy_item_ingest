"""
Module for managing and validating crawler settings.

This module provides utility classes and functions for handling the settings of
a crawler, including the database configuration, operational parameters, and
customizable options. The primary class `Settings` provides an interface for
accessing settings dynamically and offers default fallbacks where values are
not explicitly defined. Utility function `validate_settings` ensures critical
configuration is present.
"""


class Settings:
    """
    Handles settings configuration for crawlers, providing access to default values,
    database table names, and other operational parameters defined in crawler settings.

    This class facilitates the standardized management and retrieval of settings that
    are essential for database operations and crawler configurations. Its purpose
    is to provide default fallbacks and dynamically adapt to user-specified settings.
    """

    DEFAULT_ITEMS_TABLE = 'job_items'
    DEFAULT_REQUESTS_TABLE = 'job_requests'
    DEFAULT_LOGS_TABLE = 'job_logs'
    DEFAULT_TIMEZONE = "Asia/Karachi"

    def __init__(self, crawler_settings):
        self.crawler_settings = crawler_settings

    @property
    def db_url(self):
        """
        Provides access to the database URL from the crawler settings.

        This property is used to retrieve the database URL defined in the
        crawler's settings. It is helpful when a database configuration
        needs to be accessed dynamically.

        :return: The database URL as defined in the crawler's configuration
        :rtype: str or None
        """
        return self.crawler_settings.get('DB_URL')

    @property
    def db_type(self):
        """
        Retrieves the database type from the crawler settings.

        This property fetches the value assigned to the key `DB_TYPE` within
        the `crawler_settings`. Defaults to 'postgres' if the key is not set.

        :return: The database type as a string.
        :rtype: str
        """
        return self.crawler_settings.get('DB_TYPE', 'postgres')

    @property
    def db_items_table(self):
        """Return static table name for items"""
        return self.crawler_settings.get('ITEMS_TABLE', self.DEFAULT_ITEMS_TABLE)

    @property
    def db_requests_table(self):
        """
        This property fetches the name of the database table used to store request
        information. It retrieves the value from crawler settings if defined;
        otherwise, it defaults to the value of `DEFAULT_REQUESTS_TABLE`.

        :return: Name of the database table for storing requests.
        :rtype: str
        """
        return self.crawler_settings.get('REQUESTS_TABLE', self.DEFAULT_REQUESTS_TABLE)

    @property
    def db_logs_table(self):
        """
        Retrieve the name of the database logs table.

        This property fetches the value of the database logs table name
        provided in the crawler settings. If the value is not explicitly
        defined in the settings, it falls back to the default logs table.

        :return: The name of the database logs table.
        :rtype: Str
        """
        return self.crawler_settings.get('LOGS_TABLE', self.DEFAULT_LOGS_TABLE)

    @property
    def create_tables(self):
        """
        Retrieve the setting for creating database tables from crawler settings.

        This property fetches the value of the 'CREATE_TABLES' option from the crawler
        settings. If the option is not specified in the settings, it defaults to True.

        :return: Boolean value indicating whether to create tables.
        :rtype: Bool
        """
        return self.crawler_settings.getbool('CREATE_TABLES', True)

    def get_tz(self):
        """
        Return the timezone string for the project.
        This checks for a 'TIMEZONE' setting in the crawler settings and falls back to the default ('Asia/Karachi').
        Returns:
            str: The timezone string (e.g., 'Asia/Karachi').
        """
        return self.crawler_settings.get('TIMEZONE', self.DEFAULT_TIMEZONE)

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
