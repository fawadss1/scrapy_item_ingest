from setuptools import setup, find_packages

# Read the README file for long description
with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="scrapy_item_ingest",
    version="0.1.0",
    description="Scrapy extension for database ingestion with job/spider tracking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Fawad Ali",
    author_email="fawadstar6@gmail.com",
    url="https://github.com/fawadss1/scrapy_item_ingest",
    project_urls={
        "Documentation": "https://scrapy-item-ingest.readthedocs.io/",
        "Source": "https://github.com/fawadss1/scrapy_item_ingest",
        "Tracker": "https://github.com/fawadss1/scrapy_item_ingest/issues",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Scrapy",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Database",
    ],
    keywords="scrapy, database, postgresql, web-scraping, data-pipeline",
    install_requires=[
        "psycopg2-binary",
        "mysql-connector-python",
        "itemadapter",
        "SQLAlchemy"
    ],
    extras_require={
        "docs": [
            "sphinx>=5.0.0",
            "sphinx_rtd_theme>=1.2.0",
            "myst-parser>=0.18.0",
            "sphinx-autodoc-typehints>=1.19.0",
            "sphinx-copybutton>=0.5.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
            "pre-commit>=2.20.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.8.0",
        ],
    },
    entry_points={
        "scrapy.pipelines": ["db_ingest = scrapy_item_ingest.pipeline:DbInsertPipeline"],
        "scrapy.extensions": ["db_stats_logs = scrapy_item_ingest.extension:StatsAndLogExtension"],
    },
    python_requires=">=3.7",
    include_package_data=True,
    zip_safe=False,
)
