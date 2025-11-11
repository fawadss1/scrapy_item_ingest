Recipe: Scrapy logs to DB
=========================

Store Scrapy (Zyte-like) lines in ``job_logs`` with minimal noise.

1) Enable (settings.py)
-----------------------

.. code-block:: python

   EXTENSIONS = {
       'scrapy_item_ingest.LoggingExtension': 500,
   }

   # Minimum level to store
   LOG_DB_LEVEL = 'INFO'          # or 'DEBUG' for more
   # Capture level for Scrapy (DB only; console unchanged)
   LOG_DB_CAPTURE_LEVEL = 'DEBUG'

   # Allowed namespaces (defaults include [spider.name, 'scrapy'])
   # LOG_DB_LOGGERS = ['scrapy']

   # Reduce noise (defaults already exclude scraper dumps)
   # LOG_DB_EXCLUDE_LOGGERS = ['scrapy.core.scraper']
   # LOG_DB_EXCLUDE_PATTERNS = ['Scraped from <']

   # Database
   DB_URL = 'postgresql://user:password@localhost:5432/database'
   # or discrete fields
   # DB_HOST = 'localhost'
   # DB_PORT = 5432
   # DB_USER = 'user'
   # DB_PASSWORD = 'password'
   # DB_NAME = 'database'

   CREATE_TABLES = True

2) Run
------

.. code-block:: bash

   scrapy crawl your_spider

Expected
--------

- ``job_logs`` contains start/close and Scrapy framework lines (e.g., Crawled, engine events).
- No item-dump "Scraped from <...>" lines by default.

Tips
----

- To hide telnet line: add ``'scrapy.extensions.telnet'`` to ``LOG_DB_EXCLUDE_LOGGERS``.
- Keep discrete DB fields if your password has special characters.
