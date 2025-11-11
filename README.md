# Scrapy Item Ingest

A tiny, straightforward addon for Scrapy that saves your items, requests, and logs to PostgreSQL. No boilerplate, no ceremony.

## Install

```bash
pip install scrapy-item-ingest
```

## Minimal setup (settings.py)

```python
ITEM_PIPELINES = {
    'scrapy_item_ingest.DbInsertPipeline': 300,
}

EXTENSIONS = {
    'scrapy_item_ingest.LoggingExtension': 500,
}

# Pick ONE of the two database config styles:
DB_URL = "postgresql://user:password@localhost:5432/database"
# Or use discrete fields (avoids URL encoding):
# DB_HOST = "localhost"
# DB_PORT = 5432
# DB_USER = "user"
# DB_PASSWORD = "password"
# DB_NAME = "database"

# Optional
CREATE_TABLES = True     # auto‑create tables on first run (default True)
JOB_ID = 1               # or omit; spider name will be used
```

Run your spider:

```bash
scrapy crawl your_spider
```

## Troubleshooting

- Password has special characters like `@` or `$`?
  - In a URL, encode them: `@` -> `%40`, `$` -> `%24`.
  - Example: `postgresql://user:PAK%40swat1%24@localhost:5432/db`
  - Or use the discrete fields (no encoding needed).

## Useful settings (optional)

- `LOG_DB_LEVEL` (default: `DEBUG`) — minimum level stored in DB
- `LOG_DB_CAPTURE_LEVEL` — capture level for Scrapy loggers routed to DB (does not affect console)
- `LOG_DB_LOGGERS` — allowed logger prefixes (defaults always include `[spider.name, 'scrapy']`)
- `LOG_DB_EXCLUDE_LOGGERS` (default: `['scrapy.core.scraper']`)
- `LOG_DB_EXCLUDE_PATTERNS` (default: `['Scraped from <']`)
- `CREATE_TABLES` (default: `True`) — create `job_items`, `job_requests`, `job_logs` on startup
- `ITEMS_TABLE`, `REQUESTS_TABLE`, `LOGS_TABLE` — override table names

## Links

- Docs: https://scrapy-item-ingest.readthedocs.io/
- Changelog: docs/development/changelog.rst
- Issues: https://github.com/fawadss1/scrapy_item_ingest/issues

## License

MIT License. See [LICENSE](LICENSE).
