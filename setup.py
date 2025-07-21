from setuptools import setup, find_packages

setup(
    name="scrapy_item_ingest",
    version="0.2.0",
    description="Scrapy pipeline + extension to insert items, requests, stats, and logs into a relational DB",
    packages=find_packages(),
    install_requires=["psycopg2-binary", "mysql-connector-python", "itemadapter", "SQLAlchemy"],
    entry_points={
        "scrapy.pipelines": ["db_ingest = scrapy_item_ingest.pipeline:DbInsertPipeline"],
        "scrapy.extensions": ["db_stats_logs = scrapy_item_ingest.extension:StatsAndLogExtension"],
    },
    python_requires=">=3.9",
)
