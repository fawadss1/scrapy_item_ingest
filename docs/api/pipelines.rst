Pipelines API Reference
=======================

This section provides detailed API documentation for all pipeline classes in Scrapy Item Ingest.

.. currentmodule:: scrapy_item_ingest

Main Pipeline Classes
--------------------

DbInsertPipeline
~~~~~~~~~~~~~~~

.. autoclass:: DbInsertPipeline
   :members:
   :undoc-members:
   :show-inheritance:

   The main pipeline class that combines item storage and request tracking functionality.
   This is the recommended pipeline for most use cases.

   **Usage Example:**

   .. code-block:: python

      # settings.py
      ITEM_PIPELINES = {
          'scrapy_item_ingest.DbInsertPipeline': 300,
      }

   **Configuration:**

   * ``DB_URL`` - PostgreSQL connection string (required)
   * ``CREATE_TABLES`` - Whether to auto-create tables (default: True)
   * ``JOB_ID`` - Job identifier (default: spider name)

   **Methods:**

   .. method:: __init__(settings)

      Initialize the pipeline with Scrapy settings.

      :param settings: Scrapy settings object
      :type settings: scrapy.settings.Settings

   .. method:: open_spider(spider)

      Called when spider is opened. Initializes database connection and creates tables if needed.

      :param spider: The spider instance
      :type spider: scrapy.Spider

   .. method:: close_spider(spider)

      Called when spider is closed. Closes database connections and logs final statistics.

      :param spider: The spider instance
      :type spider: scrapy.Spider

   .. method:: process_item(item, spider)

      Process and store item in database.

      :param item: The scraped item
      :type item: dict or scrapy.Item
      :param spider: The spider instance
      :type spider: scrapy.Spider
      :returns: The processed item
      :rtype: dict or scrapy.Item

Individual Pipeline Components
-----------------------------

ItemsPipeline
~~~~~~~~~~~~

.. autoclass:: ItemsPipeline
   :members:
   :undoc-members:
   :show-inheritance:

   Pipeline for storing scraped items only. Use when you don't need request tracking.

   **Database Table:** ``job_items``

   **Schema:**

   .. code-block:: sql

      CREATE TABLE job_items (
          id BIGSERIAL PRIMARY KEY,
          item JSONB NOT NULL,
          created_at TIMESTAMPTZ NOT NULL,
          job_id INTEGER NOT NULL
      );

   **Usage Example:**

   .. code-block:: python

      ITEM_PIPELINES = {
          'scrapy_item_ingest.ItemsPipeline': 300,
      }

   **Methods:**

   .. method:: process_item(item, spider)

      Store item in the job_items table.

      :param item: The scraped item to store
      :param spider: The spider that scraped the item
      :returns: The original item
      :raises: Exception if database operation fails

RequestsPipeline
~~~~~~~~~~~~~~~

.. autoclass:: RequestsPipeline
   :members:
   :undoc-members:
   :show-inheritance:

   Pipeline for tracking HTTP requests and responses. Connects to Scrapy signals to capture request metadata.

   **Database Table:** ``job_requests``

   **Schema:**

   .. code-block:: sql

      CREATE TABLE job_requests (
          id BIGSERIAL PRIMARY KEY,
          url VARCHAR(200) NOT NULL,
          method VARCHAR(10) NOT NULL,
          status_code INTEGER,
          response_time FLOAT,
          fingerprint VARCHAR(255),
          parent_url VARCHAR(255),
          created_at TIMESTAMPTZ NOT NULL,
          job_id INTEGER NOT NULL,
          parent_id BIGINT,
          FOREIGN KEY (parent_id) REFERENCES job_requests(id)
      );

   **Signals Connected:**

   * ``request_scheduled`` - When request is scheduled
   * ``response_received`` - When response is received
   * ``request_dropped`` - When request is dropped

   **Methods:**

   .. method:: request_scheduled(request, spider)

      Called when a request is scheduled for downloading.

      :param request: The scheduled request
      :type request: scrapy.Request
      :param spider: The spider instance
      :type spider: scrapy.Spider

   .. method:: response_received(response, request, spider)

      Called when a response is received.

      :param response: The received response
      :type response: scrapy.Response
      :param request: The original request
      :type request: scrapy.Request
      :param spider: The spider instance
      :type spider: scrapy.Spider

   .. method:: request_dropped(request, spider)

      Called when a request is dropped.

      :param request: The dropped request
      :type request: scrapy.Request
      :param spider: The spider instance
      :type spider: scrapy.Spider

Base Classes
-----------

BasePipeline
~~~~~~~~~~~

.. autoclass:: scrapy_item_ingest.pipelines.base.BasePipeline
   :members:
   :undoc-members:
   :show-inheritance:

   Base class for all pipelines. Provides common functionality for database operations.

   **Common Methods:**

   .. method:: get_database_connection()

      Get database connection from connection pool.

      :returns: Database connection
      :rtype: psycopg2.connection
      :raises: ConnectionError if connection fails

   .. method:: create_tables_if_needed(spider)

      Create database tables if CREATE_TABLES setting is True.

      :param spider: The spider instance
      :type spider: scrapy.Spider

   .. method:: get_job_id(spider)

      Get job ID from spider or settings.

      :param spider: The spider instance
      :type spider: scrapy.Spider
      :returns: Job identifier
      :rtype: str or int

Configuration Classes
--------------------

Settings
~~~~~~~

.. autoclass:: scrapy_item_ingest.config.settings.Settings
   :members:
   :undoc-members:

   Configuration management class for pipeline settings.

   **Class Attributes:**

   .. attribute:: DB_URL

      PostgreSQL connection string. Required.

      :type: str

   .. attribute:: CREATE_TABLES

      Whether to automatically create database tables.

      :type: bool
      :default: True

   .. attribute:: JOB_ID

      Unique identifier for the crawl job.

      :type: str or int
      :default: None (uses spider name)

   .. attribute:: TABLE_ITEMS

      Name of the items table.

      :type: str
      :default: "job_items"

   .. attribute:: TABLE_REQUESTS

      Name of the requests table.

      :type: str
      :default: "job_requests"

   .. attribute:: TABLE_LOGS

      Name of the logs table.

      :type: str
      :default: "job_logs"

   **Methods:**

   .. method:: validate_settings(settings)

      Validate pipeline configuration.

      :param settings: Scrapy settings object
      :type settings: scrapy.settings.Settings
      :returns: List of validation errors
      :rtype: list
      :raises: ValueError if critical settings are missing

Database Utilities
-----------------

Connection Management
~~~~~~~~~~~~~~~~~~~

.. automodule:: scrapy_item_ingest.database.connection
   :members:
   :undoc-members:

   **Functions:**

   .. function:: get_connection(db_url, **kwargs)

      Create database connection with optional connection pooling.

      :param db_url: PostgreSQL connection string
      :type db_url: str
      :param kwargs: Additional connection parameters
      :returns: Database connection
      :rtype: psycopg2.connection

   .. function:: create_connection_pool(db_url, pool_size=10, **kwargs)

      Create connection pool for high-performance applications.

      :param db_url: PostgreSQL connection string
      :type db_url: str
      :param pool_size: Maximum number of connections in pool
      :type pool_size: int
      :returns: Connection pool
      :rtype: psycopg2.pool.SimpleConnectionPool

Schema Management
~~~~~~~~~~~~~~~

.. automodule:: scrapy_item_ingest.database.schema
   :members:
   :undoc-members:

   **Functions:**

   .. function:: create_items_table(connection, table_name="job_items")

      Create the items table with proper schema.

      :param connection: Database connection
      :type connection: psycopg2.connection
      :param table_name: Name of table to create
      :type table_name: str

   .. function:: create_requests_table(connection, table_name="job_requests")

      Create the requests table with proper schema and foreign keys.

      :param connection: Database connection
      :type connection: psycopg2.connection
      :param table_name: Name of table to create
      :type table_name: str

   .. function:: create_logs_table(connection, table_name="job_logs")

      Create the logs table with proper schema.

      :param connection: Database connection
      :type connection: psycopg2.connection
      :param table_name: Name of table to create
      :type table_name: str

Utility Functions
----------------

Data Serialization
~~~~~~~~~~~~~~~~~

.. automodule:: scrapy_item_ingest.utils.serialization
   :members:
   :undoc-members:

   **Functions:**

   .. function:: serialize_item(item)

      Serialize Scrapy item to JSON-compatible format.

      :param item: Scrapy item or dict
      :type item: scrapy.Item or dict
      :returns: JSON-serializable dictionary
      :rtype: dict
      :raises: TypeError if item contains non-serializable objects

   .. function:: clean_item_data(item)

      Clean item data for database storage.

      :param item: Raw item data
      :type item: dict
      :returns: Cleaned item data
      :rtype: dict

Request Fingerprinting
~~~~~~~~~~~~~~~~~~~~

.. automodule:: scrapy_item_ingest.utils.fingerprint
   :members:
   :undoc-members:

   **Functions:**

   .. function:: request_fingerprint(request)

      Generate unique fingerprint for request.

      :param request: Scrapy request object
      :type request: scrapy.Request
      :returns: Unique request fingerprint
      :rtype: str

   .. function:: normalize_url(url)

      Normalize URL for consistent fingerprinting.

      :param url: URL to normalize
      :type url: str
      :returns: Normalized URL
      :rtype: str

Exception Classes
----------------

Pipeline Exceptions
~~~~~~~~~~~~~~~~~

.. autoexception:: scrapy_item_ingest.exceptions.PipelineError
   :members:

   Base exception class for pipeline-related errors.

.. autoexception:: scrapy_item_ingest.exceptions.DatabaseError
   :members:

   Exception raised for database-related errors.

.. autoexception:: scrapy_item_ingest.exceptions.ConfigurationError
   :members:

   Exception raised for configuration-related errors.

.. autoexception:: scrapy_item_ingest.exceptions.SerializationError
   :members:

   Exception raised for item serialization errors.

Examples
--------

Custom Pipeline Example
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from scrapy_item_ingest.pipelines.base import BasePipeline
   from scrapy.exceptions import DropItem

   class CustomValidationPipeline(BasePipeline):
       """Custom pipeline that extends base functionality"""

       def __init__(self, settings):
           super().__init__(settings)
           self.required_fields = ['title', 'url']
           self.max_title_length = 200

       def process_item(self, item, spider):
           # Validate required fields
           for field in self.required_fields:
               if not item.get(field):
                   raise DropItem(f"Missing required field: {field}")

           # Validate field lengths
           if len(item.get('title', '')) > self.max_title_length:
               item['title'] = item['title'][:self.max_title_length]
               spider.logger.warning(f"Truncated title for {item['url']}")

           # Add metadata
           item['processed_by'] = self.__class__.__name__
           item['validation_passed'] = True

           return item

Advanced Configuration Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from scrapy_item_ingest import DbInsertPipeline, Settings

   class ProductionPipeline(DbInsertPipeline):
       """Production-optimized pipeline with custom settings"""

       def __init__(self, settings):
           # Override default settings
           production_settings = Settings()
           production_settings.DB_SETTINGS = {
               'pool_size': 20,
               'max_overflow': 30,
               'pool_timeout': 30,
           }
           production_settings.BATCH_SIZE = 1000

           super().__init__(production_settings)

       def process_item(self, item, spider):
           # Add production-specific metadata
           item['environment'] = 'production'
           item['pipeline_version'] = '2.0'

           return super().process_item(item, spider)

See Also
--------

* :doc:`../user-guide/pipelines` - User guide for pipelines
* :doc:`../user-guide/database-schema` - Database schema reference
* :doc:`../examples/advanced-configurations` - Advanced usage examples
