Scrapy Item Ingest Documentation
==================================

**A comprehensive Scrapy extension for ingesting scraped items, requests, and logs into PostgreSQL databases with advanced tracking capabilities.**

.. image:: https://img.shields.io/badge/python-3.7+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python 3.7+

.. image:: https://img.shields.io/badge/database-PostgreSQL-blue.svg
   :target: https://www.postgresql.org/
   :alt: PostgreSQL

.. image:: https://img.shields.io/badge/license-MIT-green.svg
   :target: https://github.com/fawadss1/scrapy_item_ingest/blob/main/LICENSE
   :alt: License

Welcome to the documentation for **Scrapy Item Ingest**, a powerful extension that seamlessly integrates your Scrapy spiders with PostgreSQL databases for comprehensive data storage and tracking.

🚀 Key Features
--------------

* **Real-time Data Ingestion**: Store items, requests, and logs as they're processed
* **Request Tracking**: Track request response times, fingerprints, and parent-child relationships
* **Comprehensive Logging**: Capture spider events, errors, and custom messages
* **Flexible Schema**: Support for both auto-creation and existing table modes
* **Modular Design**: Use individual components or the complete pipeline
* **Production Ready**: Handles both development and production scenarios
* **JSONB Storage**: Store complex item data as JSONB for flexible querying

📚 Documentation Structure
-------------------------

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart
   configuration

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user-guide/pipelines
   user-guide/extensions
   user-guide/database-schema
   user-guide/advanced-usage

.. toctree::
   :maxdepth: 2
   :caption: Examples

   examples/basic-setup
   examples/advanced-configurations
   examples/production-deployment
   examples/troubleshooting

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/pipelines
   api/extensions
   api/configuration
   api/utilities

.. toctree::
   :maxdepth: 1
   :caption: Development

   development/contributing
   development/changelog
   development/roadmap

🔗 Quick Links
--------------

* :doc:`installation` - Get started with installation
* :doc:`quickstart` - Basic usage examples
* :doc:`user-guide/pipelines` - Pipeline components
* :doc:`api/pipelines` - API reference
* `GitHub Repository <https://github.com/fawadss1/scrapy_item_ingest>`_

💡 Need Help?
------------

* Check out the :doc:`examples/troubleshooting` section
* Review the :doc:`api/pipelines` for detailed API documentation
* Visit our `GitHub Issues <https://github.com/fawadss1/scrapy_item_ingest/issues>`_ page

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
