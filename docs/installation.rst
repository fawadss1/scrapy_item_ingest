Installation
============

This guide will walk you through installing Scrapy Item Ingest and its dependencies.

Requirements
-----------

* Python 3.7 or higher
* PostgreSQL database
* Scrapy framework

Dependencies
-----------

Scrapy Item Ingest automatically installs the following dependencies:

* ``psycopg2-binary`` - PostgreSQL adapter for Python
* ``mysql-connector-python`` - MySQL connector (for future MySQL support)
* ``itemadapter`` - Scrapy item handling utilities
* ``SQLAlchemy`` - SQL toolkit and ORM

Installation Methods
-------------------

PyPI Installation (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install scrapy-item-ingest

Development Installation
~~~~~~~~~~~~~~~~~~~~~~~

To install from source for development:

.. code-block:: bash

   git clone https://github.com/fawadss1/scrapy_item_ingest.git
   cd scrapy_item_ingest
   pip install -e .

Docker Installation
~~~~~~~~~~~~~~~~~~

If you're using Docker, add this to your ``requirements.txt``:

.. code-block:: text

   scrapy-item-ingest==0.1.2

Virtual Environment Setup
~~~~~~~~~~~~~~~~~~~~~~~~~

We recommend using a virtual environment:

.. code-block:: bash

   # Create virtual environment
   python -m venv scrapy_env

   # Activate virtual environment
   # On Windows:
   scrapy_env\Scripts\activate
   # On macOS/Linux:
   source scrapy_env/bin/activate

   # Install scrapy-item-ingest
   pip install scrapy-item-ingest

Database Setup
-------------

PostgreSQL Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

1. **Install PostgreSQL** (if not already installed):

   .. code-block:: bash

      # Ubuntu/Debian
      sudo apt-get install postgresql postgresql-contrib

      # macOS with Homebrew
      brew install postgresql

      # Windows: Download from https://www.postgresql.org/download/

2. **Create a database**:

   .. code-block:: sql

      -- Connect to PostgreSQL as superuser
      sudo -u postgres psql

      -- Create database
      CREATE DATABASE scrapy_data;

      -- Create user (optional)
      CREATE USER scrapy_user WITH PASSWORD 'your_password';
      GRANT ALL PRIVILEGES ON DATABASE scrapy_data TO scrapy_user;

3. **Test connection**:

   .. code-block:: bash

      psql postgresql://scrapy_user:your_password@localhost:5432/scrapy_data

Verification
-----------

After installation, verify that everything is working:

.. code-block:: python

   # Test import
   try:
       from scrapy_item_ingest import DbInsertPipeline, LoggingExtension
       print("✅ Installation successful!")
   except ImportError as e:
       print(f"❌ Installation failed: {e}")

   # Test database connection
   import psycopg2
   try:
       conn = psycopg2.connect(
           "postgresql://username:password@localhost:5432/database_name"
       )
       print("✅ Database connection successful!")
       conn.close()
   except Exception as e:
       print(f"❌ Database connection failed: {e}")

Troubleshooting
--------------

Common Installation Issues
~~~~~~~~~~~~~~~~~~~~~~~~~

**psycopg2 installation error:**

.. code-block:: bash

   # Install system dependencies first
   # Ubuntu/Debian:
   sudo apt-get install libpq-dev python3-dev

   # macOS:
   brew install postgresql

   # Then reinstall
   pip install psycopg2-binary

**Permission denied errors:**

.. code-block:: bash

   # Use user installation
   pip install --user scrapy-item-ingest

**Virtual environment issues:**

.. code-block:: bash

   # Ensure virtual environment is activated
   which python  # Should point to your virtual environment

   # Upgrade pip first
   pip install --upgrade pip

Next Steps
---------

Once installation is complete, proceed to:

* :doc:`quickstart` - Basic usage examples
* :doc:`configuration` - Configuration options
* :doc:`user-guide/pipelines` - Detailed pipeline documentation
