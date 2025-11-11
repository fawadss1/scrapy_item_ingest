Quick Start
===========

Get running in minutes.

1) Install
----------

.. code-block:: bash

   pip install scrapy-item-ingest

2) Enable (settings.py)
-----------------------

.. code-block:: python

   ITEM_PIPELINES = {
       'scrapy_item_ingest.DbInsertPipeline': 300,
   }

   EXTENSIONS = {
       'scrapy_item_ingest.LoggingExtension': 500,
   }

   # EITHER a single URL
   DB_URL = 'postgresql://user:password@localhost:5432/database'
   # OR discrete fields (no URL encoding needed)
   # DB_HOST = 'localhost'
   # DB_PORT = 5432
   # DB_USER = 'user'
   # DB_PASSWORD = 'password'
   # DB_NAME = 'database'

   # Optional
   CREATE_TABLES = True
   # JOB_ID = 1  # or omit to use spider name

3) Run
------

.. code-block:: bash

   scrapy crawl your_spider

4) Verify
---------

Data is written into these tables (created automatically when `CREATE_TABLES = True`):

- `job_items`
- `job_requests`
- `job_logs`

5) Troubleshooting
------------------

- Password contains `@` or `$`? If using `DB_URL`, encode them (`@` -> `%40`, `$` -> `%24`).
- Or use discrete fields to avoid encoding.

That's it.
