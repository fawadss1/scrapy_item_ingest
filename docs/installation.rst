Installation
============

Requirements
------------

- Python 3.8+
- Scrapy
- PostgreSQL

Install from PyPI
-----------------

.. code-block:: bash

   pip install scrapy-item-ingest

Minimal configuration (settings.py)
----------------------------------

.. code-block:: python

   ITEM_PIPELINES = {
       'scrapy_item_ingest.DbInsertPipeline': 300,
   }

   EXTENSIONS = {
       'scrapy_item_ingest.LoggingExtension': 500,
   }

   # Pick ONE of the two database config styles:
   DB_URL = "postgresql://user:password@localhost:5432/database"
   # Or use discrete fields (no URL encoding needed):
   # DB_HOST = "localhost"
   # DB_PORT = 5432
   # DB_USER = "user"
   # DB_PASSWORD = "password"
   # DB_NAME = "database"

   # Optional
   CREATE_TABLES = True
   # JOB_ID = 1  # or omit to use spider name

Run
---

.. code-block:: bash

   scrapy crawl your_spider

Troubleshooting
---------------

- If your password contains special characters (e.g., `@`, `$`) and you use `DB_URL`, URL‑encode them.
  - Example: `PAK@swat1$` -> `PAK%40swat1%24`
- Or use the discrete fields to avoid URL encoding entirely.

Next steps
----------

- :doc:`quickstart`
- :doc:`configuration`
- :doc:`examples/troubleshooting`
