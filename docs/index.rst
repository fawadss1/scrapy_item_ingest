Scrapy Item Ingest
===================

Save your Scrapy items, requests, and logs to PostgreSQL with a minimal setup.

Quick Start
-----------

1) Install
~~~~~~~~~~

.. code-block:: bash

   pip install scrapy-item-ingest

2) Enable in settings.py
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   ITEM_PIPELINES = {
       'scrapy_item_ingest.DbInsertPipeline': 300,
   }

   EXTENSIONS = {
       'scrapy_item_ingest.LoggingExtension': 500,
   }

   # Pick ONE of the two database config styles:
   DB_URL = "postgresql://user:password@localhost:5432/database"
   # Or discrete fields (no URL encoding needed):
   # DB_HOST = "localhost"
   # DB_PORT = 5432
   # DB_USER = "user"
   # DB_PASSWORD = "password"
   # DB_NAME = "database"

   # Optional
   CREATE_TABLES = True
   # JOB_ID = 1  # or omit to use spider name

3) Run
~~~~~~

.. code-block:: bash

   scrapy crawl your_spider

Notes
-----

- If your password contains @ or $, URL‑encode them in `DB_URL` (e.g., `PAK@swat1$` -> `PAK%40swat1%24`).
- Or use the discrete fields above to avoid encoding entirely.

Docs
----
.. toctree::
   :maxdepth: 1

   installation
   quickstart
   configuration
   examples/recipes-basic
   examples/recipes-items-only
   examples/recipes-requests
   examples/recipes-db-logging
   examples/troubleshooting
   development/changelog

Links
-----

- GitHub: https://github.com/fawadss1/scrapy_item_ingest
- License: MIT
