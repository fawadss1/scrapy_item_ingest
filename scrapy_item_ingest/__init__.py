"""
scrapy_item_ingest - A Scrapy extension for ingesting items and requests into databases.

This package provides pipelines and extensions for storing scraped data, tracking requests,
and logging spider events to PostgreSQL databases with support for both spider-based and
job-based identification.

Main Components:
- DbInsertPipeline: Combined pipeline for items and requests
- LoggingExtension: Extension for logging spider events
- ItemsPipeline: Standalone items processing pipeline
- RequestsPipeline: Standalone requests tracking pipeline
"""

__version__ = "0.1.2"
__author__ = "Fawad Ali"
__description__ = "Scrapy extension for database ingestion with job/spider tracking"

# Import main classes directly from organized modules
from .pipelines.main import DbInsertPipeline
from .extensions.logging import LoggingExtension

# Import individual components for advanced users
from .pipelines.items import ItemsPipeline
from .pipelines.requests import RequestsPipeline

# Import configuration utilities
from .config.settings import Settings, validate_settings

# Define what gets imported with "from scrapy_item_ingest import *"
__all__ = [
    # Main classes (most commonly used)
    'DbInsertPipeline',
    'LoggingExtension',

    # Individual components
    'ItemsPipeline',
    'RequestsPipeline',

    # Configuration
    'Settings',
    'validate_settings',

    # Package metadata
    '__version__',
    '__author__',
    '__description__',
]
