Quick Start
===========

Get up and running with Scrapy Item Ingest in minutes. This guide covers the most common use cases and basic configuration.

Basic Setup
-----------

1. **Add to your Scrapy project's** ``settings.py``:

.. code-block:: python

   # Enable the main pipeline and logging extension
   ITEM_PIPELINES = {
       'scrapy_item_ingest.DbInsertPipeline': 300,
   }

   EXTENSIONS = {
       'scrapy_item_ingest.LoggingExtension': 500,
   }

   # Database configuration
   DB_URL = 'postgresql://username:password@localhost:5432/database_name'

   # Optional: Auto-create tables (default: True)
   CREATE_TABLES = True

   # Optional: Job identifier (uses spider name if not provided)
   JOB_ID = 'my_crawl_job_001'

2. **Run your spider** as usual:

.. code-block:: bash

   scrapy crawl your_spider_name

That's it! Your items, requests, and logs will automatically be stored in PostgreSQL.

Example Spider
--------------

Here's a complete example spider that works with Scrapy Item Ingest:

.. code-block:: python

   import scrapy
   from scrapy import Item, Field

   class ProductItem(Item):
       name = Field()
       price = Field()
       description = Field()
       url = Field()

   class ExampleSpider(scrapy.Spider):
       name = 'example'
       start_urls = ['https://example.com/products']

       def parse(self, response):
           # Extract product links
           product_links = response.css('.product-link::attr(href)').getall()

           for link in product_links:
               yield response.follow(link, self.parse_product)

       def parse_product(self, response):
           # Extract product data
           yield ProductItem(
               name=response.css('h1::text').get(),
               price=response.css('.price::text').get(),
               description=response.css('.description::text').get(),
               url=response.url
           )

Configuration Examples
----------------------

Development Mode
~~~~~~~~~~~~~~~

Perfect for development with automatic table creation:

.. code-block:: python

   # settings.py
   ITEM_PIPELINES = {
       'scrapy_item_ingest.DbInsertPipeline': 300,
   }

   EXTENSIONS = {
       'scrapy_item_ingest.LoggingExtension': 500,
   }

   DB_URL = 'postgresql://dev_user:dev_pass@localhost:5432/dev_scrapy'
   CREATE_TABLES = True
   JOB_ID = 'dev_crawl_20250721_001'

Production Mode
~~~~~~~~~~~~~~

For production with existing tables:

.. code-block:: python

   # settings.py
   ITEM_PIPELINES = {
       'scrapy_item_ingest.DbInsertPipeline': 300,
   }

   EXTENSIONS = {
       'scrapy_item_ingest.LoggingExtension': 500,
   }

   DB_URL = 'postgresql://prod_user:prod_pass@prod-db:5432/scrapy_data'
   CREATE_TABLES = False  # Tables must already exist
   JOB_ID = 'prod_job_001'

Individual Components
~~~~~~~~~~~~~~~~~~~~

Use only specific components if needed:

.. code-block:: python

   # Only store items (no request tracking)
   ITEM_PIPELINES = {
       'scrapy_item_ingest.ItemsPipeline': 300,
   }

   # Only track requests (no item storage)
   ITEM_PIPELINES = {
       'scrapy_item_ingest.RequestsPipeline': 310,
   }

   # Only logging (no pipelines)
   EXTENSIONS = {
       'scrapy_item_ingest.LoggingExtension': 500,
   }

Database Schema Overview
-----------------------

The extension automatically creates three tables:

**Items Table** (``job_items``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Stores all scraped items as JSONB:

.. code-block:: sql

   CREATE TABLE job_items (
       id BIGSERIAL PRIMARY KEY,
       item JSONB NOT NULL,
       created_at TIMESTAMPTZ NOT NULL,
       job_id INTEGER NOT NULL
   );

**Requests Table** (``job_requests``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tracks all requests and responses:

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
       parent_id BIGINT
   );

**Logs Table** (``job_logs``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Captures spider events and messages:

.. code-block:: sql

   CREATE TABLE job_logs (
       id BIGSERIAL PRIMARY KEY,
       job_id INTEGER NOT NULL,
       type VARCHAR(50) NOT NULL,
       message TEXT NOT NULL,
       created_at TIMESTAMPTZ NOT NULL
   );

Querying Your Data
------------------

Once your spider runs, you can query the data:

.. code-block:: sql

   -- View all items for a specific job
   SELECT item, created_at
   FROM job_items
   WHERE job_id = 1
   ORDER BY created_at DESC;

   -- Check request performance
   SELECT url, status_code, response_time, created_at
   FROM job_requests
   WHERE job_id = 1
   ORDER BY response_time DESC;

   -- Review logs
   SELECT type, message, created_at
   FROM job_logs
   WHERE job_id = 1
   ORDER BY created_at DESC;

   -- Extract specific fields from JSONB items
   SELECT
       item->>'name' as product_name,
       item->>'price' as product_price,
       created_at
   FROM job_items
   WHERE job_id = 1;

Common Use Cases
---------------

Monitoring Spider Performance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sql

   -- Average response time by domain
   SELECT
       SPLIT_PART(url, '/', 3) as domain,
       AVG(response_time) as avg_response_time,
       COUNT(*) as request_count
   FROM job_requests
   WHERE job_id = 1
   GROUP BY domain;

Analyzing Scraped Data
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sql

   -- Find items with specific attributes
   SELECT item
   FROM job_items
   WHERE job_id = 1
   AND item->>'price' IS NOT NULL;

   -- Count items by category
   SELECT
       item->>'category' as category,
       COUNT(*) as item_count
   FROM job_items
   WHERE job_id = 1
   GROUP BY category;

Error Analysis
~~~~~~~~~~~~~

.. code-block:: sql

   -- Find failed requests
   SELECT url, status_code, created_at
   FROM job_requests
   WHERE job_id = 1
   AND status_code >= 400;

   -- Review error logs
   SELECT message, created_at
   FROM job_logs
   WHERE job_id = 1
   AND type = 'ERROR';

Next Steps
----------

* :doc:`configuration` - Detailed configuration options
* :doc:`user-guide/pipelines` - Deep dive into pipeline components
* :doc:`user-guide/database-schema` - Complete database schema reference
* :doc:`examples/advanced-configurations` - Advanced usage patterns
