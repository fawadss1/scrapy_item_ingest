Recipe: Requests tracking
=========================

Track scheduled/received requests with parent linkage and response time.

1) Enable (settings.py)
-----------------------

.. code-block:: python

   ITEM_PIPELINES = {
       'scrapy_item_ingest.RequestsPipeline': 300,
   }

   # Database
   DB_URL = 'postgresql://user:password@localhost:5432/database'
   # or discrete fields
   # DB_HOST = 'localhost'
   # DB_PORT = 5432
   # DB_USER = 'user'
   # DB_PASSWORD = 'password'
   # DB_NAME = 'database'

   CREATE_TABLES = True

2) What it logs
---------------

- URL, method
- status_code (when response received)
- response_time (seconds)
- fingerprint
- parent_id / parent_url (when known)

3) Run
------

.. code-block:: bash

   scrapy crawl your_spider

Expected
--------

- Rows in ``job_requests`` with ``parent_id`` filled when parent known.
- Items table untouched in this recipe (no ItemsPipeline).

Tip
---

Start with a small crawl to verify parent linkage before scaling.
