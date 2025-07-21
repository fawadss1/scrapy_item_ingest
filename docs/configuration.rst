Configuration
=============

This guide covers all configuration options available in Scrapy Item Ingest, from basic setup to advanced customization.

Core Settings
-------------

Database Configuration
~~~~~~~~~~~~~~~~~~~~~

**DB_URL** (Required)
  PostgreSQL connection string

  .. code-block:: python

     # Basic format
     DB_URL = 'postgresql://username:password@host:port/database'

     # Examples
     DB_URL = 'postgresql://scrapy:mypass@localhost:5432/scrapy_data'
     DB_URL = 'postgresql://user:pass@db.example.com:5432/production_db'

     # With SSL
     DB_URL = 'postgresql://user:pass@host:5432/db?sslmode=require'

**CREATE_TABLES** (Optional, default: ``True``)
  Whether to automatically create database tables

  .. code-block:: python

     # Development mode - auto-create tables
     CREATE_TABLES = True

     # Production mode - use existing tables
     CREATE_TABLES = False

**JOB_ID** (Optional, default: ``None``)
  Unique identifier for the crawl job

  .. code-block:: python

     # Explicit job ID
     JOB_ID = 'crawl_20250721_001'

     # Auto-generated from spider name (if None)
     JOB_ID = None  # Will use spider.name

Pipeline Configuration
~~~~~~~~~~~~~~~~~~~~~

**ITEM_PIPELINES**
  Configure which pipelines to use and their order

  .. code-block:: python

     # Complete functionality
     ITEM_PIPELINES = {
         'scrapy_item_ingest.DbInsertPipeline': 300,
     }

     # Items only
     ITEM_PIPELINES = {
         'scrapy_item_ingest.ItemsPipeline': 300,
     }

     # Requests only
     ITEM_PIPELINES = {
         'scrapy_item_ingest.RequestsPipeline': 310,
     }

     # Both separately (for custom configurations)
     ITEM_PIPELINES = {
         'scrapy_item_ingest.ItemsPipeline': 300,
         'scrapy_item_ingest.RequestsPipeline': 310,
     }

Extension Configuration
~~~~~~~~~~~~~~~~~~~~~~

**EXTENSIONS**
  Configure logging and monitoring extensions

  .. code-block:: python

     # Enable logging extension
     EXTENSIONS = {
         'scrapy_item_ingest.LoggingExtension': 500,
     }

Advanced Settings
----------------

Database Connection Pooling
~~~~~~~~~~~~~~~~~~~~~~~~~~~

For high-throughput spiders, configure connection pooling:

.. code-block:: python

   # Custom database settings (advanced)
   DB_SETTINGS = {
       'pool_size': 10,
       'max_overflow': 20,
       'pool_timeout': 30,
       'pool_recycle': 3600,
   }

Table Naming
~~~~~~~~~~~

Customize table names (if needed):

.. code-block:: python

   # Default table names
   TABLE_ITEMS = 'job_items'
   TABLE_REQUESTS = 'job_requests'
   TABLE_LOGS = 'job_logs'

   # Custom table names
   TABLE_ITEMS = 'custom_items'
   TABLE_REQUESTS = 'custom_requests'
   TABLE_LOGS = 'custom_logs'

Environment-Specific Configurations
-----------------------------------

Development Environment
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # settings/development.py
   from .base import *

   # Database
   DB_URL = 'postgresql://dev_user:dev_pass@localhost:5432/dev_scrapy'
   CREATE_TABLES = True
   JOB_ID = f'dev_{spider.name}_{int(time.time())}'

   # Pipelines
   ITEM_PIPELINES = {
       'scrapy_item_ingest.DbInsertPipeline': 300,
   }

   EXTENSIONS = {
       'scrapy_item_ingest.LoggingExtension': 500,
   }

   # Debug settings
   LOG_LEVEL = 'DEBUG'

Staging Environment
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # settings/staging.py
   from .base import *

   # Database
   DB_URL = 'postgresql://staging_user:staging_pass@staging-db:5432/scrapy_staging'
   CREATE_TABLES = True  # Can auto-create in staging
   JOB_ID = f'staging_{spider.name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

   # Pipelines
   ITEM_PIPELINES = {
       'scrapy_item_ingest.DbInsertPipeline': 300,
   }

   EXTENSIONS = {
       'scrapy_item_ingest.LoggingExtension': 500,
   }

   LOG_LEVEL = 'INFO'

Production Environment
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # settings/production.py
   from .base import *
   import os

   # Database (from environment variables)
   DB_URL = os.getenv('DATABASE_URL', 'postgresql://user:pass@prod-db:5432/scrapy_prod')
   CREATE_TABLES = False  # Tables must exist in production
   JOB_ID = os.getenv('JOB_ID', f'prod_{spider.name}_{int(time.time())}')

   # Pipelines
   ITEM_PIPELINES = {
       'scrapy_item_ingest.DbInsertPipeline': 300,
   }

   EXTENSIONS = {
       'scrapy_item_ingest.LoggingExtension': 500,
   }

   # Production settings
   LOG_LEVEL = 'WARNING'
   TELNETCONSOLE_ENABLED = False

Configuration Validation
------------------------

Validate your configuration before running:

.. code-block:: python

   # In your spider or settings
   from scrapy_item_ingest import validate_settings

   def validate_config(settings):
       """Validate configuration before spider starts"""
       errors = validate_settings(settings)
       if errors:
           raise ValueError(f"Configuration errors: {errors}")

Environment Variables
--------------------

Use environment variables for sensitive configuration:

.. code-block:: bash

   # .env file
   DATABASE_URL=postgresql://user:password@host:5432/database
   JOB_ID=production_job_001
   CREATE_TABLES=false

.. code-block:: python

   # settings.py
   import os
   from dotenv import load_dotenv

   load_dotenv()

   DB_URL = os.getenv('DATABASE_URL')
   JOB_ID = os.getenv('JOB_ID')
   CREATE_TABLES = os.getenv('CREATE_TABLES', 'true').lower() == 'true'

Docker Configuration
-------------------

For containerized deployments:

.. code-block:: yaml

   # docker-compose.yml
   version: '3.8'
   services:
     scrapy:
       build: .
       environment:
         - DATABASE_URL=postgresql://scrapy:password@postgres:5432/scrapy_data
         - JOB_ID=docker_job_001
         - CREATE_TABLES=true
       depends_on:
         - postgres

     postgres:
       image: postgres:13
       environment:
         - POSTGRES_DB=scrapy_data
         - POSTGRES_USER=scrapy
         - POSTGRES_PASSWORD=password

.. code-block:: dockerfile

   # Dockerfile
   FROM python:3.9-slim

   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt

   COPY . .
   CMD ["scrapy", "crawl", "your_spider"]

Troubleshooting Configuration
----------------------------

Common Configuration Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Database Connection Failed:**

.. code-block:: python

   # Test connection before running spider
   import psycopg2

   try:
       conn = psycopg2.connect(DB_URL)
       print("✅ Database connection successful")
       conn.close()
   except Exception as e:
       print(f"❌ Database connection failed: {e}")

**Table Creation Issues:**

.. code-block:: python

   # Check if tables exist
   CREATE_TABLES = True  # Enable auto-creation

   # Or create manually:
   # See database-schema.rst for SQL commands

**Pipeline Order Issues:**

.. code-block:: python

   # Ensure correct pipeline order (lower numbers run first)
   ITEM_PIPELINES = {
       'scrapy_item_ingest.DbInsertPipeline': 300,  # Run this first
       'myproject.pipelines.CustomPipeline': 400,   # Then custom pipelines
   }

Configuration Best Practices
----------------------------

1. **Use Environment-Specific Settings Files**

   .. code-block:: bash

      scrapy crawl spider -s SCRAPY_SETTINGS_MODULE=myproject.settings.production

2. **Validate Configuration on Startup**

   .. code-block:: python

      # In spider's __init__ or start_requests
      self.validate_configuration()

3. **Use Environment Variables for Secrets**

   .. code-block:: python

      # Never hardcode passwords in settings
      DB_URL = os.getenv('DATABASE_URL')

4. **Test Configuration in Development**

   .. code-block:: python

      # Test with small dataset first
      CLOSESPIDER_ITEMCOUNT = 100  # Limit items in dev

5. **Monitor Configuration in Production**

   .. code-block:: python

      # Log important configuration values (without secrets)
      logger.info(f"Using job_id: {JOB_ID}")
      logger.info(f"Create tables: {CREATE_TABLES}")

Next Steps
----------

* :doc:`user-guide/pipelines` - Understanding pipeline components
* :doc:`user-guide/database-schema` - Database schema details
* :doc:`examples/advanced-configurations` - Real-world configuration examples
