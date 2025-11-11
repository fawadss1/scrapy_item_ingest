Configuration
=============

Essential settings only. Add these to your Scrapy project's settings.py.

Required
--------

- Database (pick ONE style)

.. code-block:: python

   # Single URL
   DB_URL = 'postgresql://user:password@localhost:5432/database'

   # OR discrete fields (no URL encoding needed)
   # DB_HOST = 'localhost'
   # DB_PORT = 5432
   # DB_USER = 'user'
   # DB_PASSWORD = 'password'
   # DB_NAME = 'database'

Recommended
-----------

.. code-block:: python

   ITEM_PIPELINES = {
       'scrapy_item_ingest.DbInsertPipeline': 300,
   }

   EXTENSIONS = {
       'scrapy_item_ingest.LoggingExtension': 500,
   }

Optional
--------

.. code-block:: python

   CREATE_TABLES = True   # auto-create job_items, job_requests, job_logs
   # JOB_ID = 1           # omit to use spider name

Table names (optional)
----------------------

.. code-block:: python

   # Defaults
   # ITEMS_TABLE = 'job_items'
   # REQUESTS_TABLE = 'job_requests'
   # LOGS_TABLE = 'job_logs'

Logging to DB (optional)
------------------------

.. code-block:: python

   # Minimum level stored in DB
   # LOG_DB_LEVEL = 'INFO'  # or 'DEBUG', 'WARNING', ...

   # Capture level for Scrapy loggers routed to DB (does not change console)
   # LOG_DB_CAPTURE_LEVEL = 'DEBUG'

   # Include/exclude loggers and messages
   # LOG_DB_LOGGERS = ['scrapy']
   # LOG_DB_EXCLUDE_LOGGERS = ['scrapy.core.scraper']
   # LOG_DB_EXCLUDE_PATTERNS = ['Scraped from <']

Tips
----

- Password has `@` or `$`? If using `DB_URL`, encode them: `@` -> `%40`, `$` -> `%24`.
- Prefer discrete fields to avoid URL encoding.
- Set `CREATE_TABLES = True` for the first run, then keep or turn off as you prefer.
