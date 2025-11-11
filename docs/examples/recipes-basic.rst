Basic Recipe: Items + Requests + Logs
====================================

The fastest way to store items, requests, and Scrapy logs in PostgreSQL.

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

   # Either one URL
   DB_URL = 'postgresql://user:password@localhost:5432/database'
   # or discrete fields (no URL encoding)
   # DB_HOST = 'localhost'
   # DB_PORT = 5432
   # DB_USER = 'user'
   # DB_PASSWORD = 'password'
   # DB_NAME = 'database'

   CREATE_TABLES = True   # auto-create tables on first run
   # JOB_ID = 1           # optional; spider name if omitted

3) Run
------

.. code-block:: bash

   scrapy crawl your_spider

Expected tables
---------------

- ``job_items``: JSON items
- ``job_requests``: requests with parent/response_time
- ``job_logs``: spider + selected Scrapy lines

Tips
----

- Password contains ``@`` or ``$``? In URLs encode: ``@`` -> ``%40``, ``$`` -> ``%24``.
- Prefer discrete DB fields to avoid encoding entirely.
