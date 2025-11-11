# Scrapy Item Ingest

[![PyPI Version](https://img.shields.io/pypi/v/scrapy-item-ingest.svg)](https://pypi.org/project/scrapy-item-ingest/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/scrapy-item-ingest.svg)](https://pypi.org/project/scrapy-item-ingest/)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/scrapy-item-ingest.svg)](https://pypi.org/project/scrapy-item-ingest/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![GitHub Stars](https://img.shields.io/github/stars/fawadss1/scrapy_item_ingest.svg)](https://github.com/fawadss1/scrapy_item_ingest/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/fawadss1/scrapy_item_ingest.svg)](https://github.com/fawadss1/scrapy_item_ingest/issues)
[![GitHub Last Commit](https://img.shields.io/github/last-commit/fawadss1/scrapy_item_ingest.svg)](https://github.com/fawadss1/scrapy_item_ingest/commits)

A comprehensive Scrapy extension for ingesting scraped items, requests, and logs into PostgreSQL databases with advanced tracking capabilities. This library provides a clean, production-ready solution for storing and monitoring your Scrapy crawling operations with real-time data ingestion and comprehensive logging.

## Documentation

Full documentation is available at: [https://scrapy-item-ingest.readthedocs.io/en/latest/](https://scrapy-item-ingest.readthedocs.io/en/latest/)

## Key Features

- 🔄 **Real-time Data Ingestion**: Store items, requests, and logs as they're processed
- 📊 **Request Tracking**: Track request response times, fingerprints, and parent-child relationships
- 🔍 **Comprehensive Logging**: Capture spider events, errors, and custom messages
- 🏗️ **Flexible Schema**: Support for both auto-creation and existing table modes
- ⚙️ **Modular Design**: Use individual components or the complete pipeline
- 🛡️ **Production Ready**: Handles both development and production scenarios
- 📝 **JSONB Storage**: Store complex item data as JSONB for flexible querying
- 🐳 **Docker Support**: Complete containerization with Docker and Kubernetes
- 📈 **Performance Optimized**: Connection pooling and batch processing
- 🔧 **Easy Configuration**: Environment-based configuration with validation
- 📊 **Monitoring Ready**: Built-in metrics and health checks

## Installation

```bash
pip install scrapy-item-ingest
```

## Development

### Setting up for Development

```bash
git clone https://github.com/fawadss1/scrapy_item_ingest.git
cd scrapy_item_ingest
pip install -e ".[dev]"
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:

- **Email**: fawadstar6@gmail.com
- **Documentation**: [https://scrapy-item-ingest.readthedocs.io/](https://scrapy-item-ingest.readthedocs.io/)
- **Issues**: Please report bugs and feature requests at [GitHub Issues](https://github.com/fawadss1/scrapy_item_ingest/issues)

## Changelog

### v0.2.0 (2025-11-11) — Current

- Database connection: automatic DSN normalization to safely handle special characters in credentials (e.g., `@`, `$`) without modifying your settings
- Unified DB access across pipelines and extensions via `DatabaseConnection` (singleton) with `connect/execute/commit/rollback/close`
- Logging extension overhaul:
  - Capture Scrapy default (framework) logs in addition to spider logs
  - Attach DB handler to spider logger and top-level `scrapy` logger only to avoid duplicates via propagation
  - Console-like formatting using `LOG_FORMAT` and `LOG_DATEFORMAT`
  - Fine-grained filtering: allowlist by logger namespaces plus exclusions by logger and message substrings
  - Built-in de-duplication to suppress repeated lines within a small time window
  - Error throttling to stop DB logging after the first write failure (prevents spam)
- Schema consistency: logs table consistently uses `level` column (not `type`)
- Backwards compatibility: `DatabaseConnection` remains alias to `DBConnection`

New optional settings:
- `LOG_DB_LEVEL` (default: `DEBUG`) — minimum level stored in DB
- `LOG_DB_CAPTURE_LEVEL` (default: same as `LOG_DB_LEVEL`) — capture level for attached loggers (DB only; does not affect console)
- `LOG_DB_LOGGERS` — additional allowed logger prefixes (defaults always include `[spider.name, 'scrapy']`)
- `LOG_DB_EXCLUDE_LOGGERS` (default: `['scrapy.core.scraper']`)
- `LOG_DB_EXCLUDE_PATTERNS` (default: `['Scraped from <']`)
- `LOG_DB_BATCH_SIZE` — batch size for DB inserts
- `LOG_DB_DEDUP_TTL` — seconds to suppress duplicate messages

### v0.1.2

- Initial release
- Core pipeline functionality for items, requests, and logs
- PostgreSQL database integration with JSONB storage
- Comprehensive documentation and examples
- Production deployment guides
- Docker and Kubernetes support
