# scrapy_item_ingest 🕷️📊

**A comprehensive Scrapy extension for ingesting scraped items, requests, and logs into PostgreSQL databases with advanced tracking capabilities.**

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 🚀 Features

- **🔄 Real-time Data Ingestion**: Store items, requests, and logs as they're processed
- **📊 Request Tracking**: Track request response times, fingerprints, and parent-child relationships
- **🔍 Comprehensive Logging**: Capture spider events, errors, and custom messages
- **🏗️ Flexible Schema**: Support for both auto-creation and existing table modes
- **⚙️ Modular Design**: Use individual components or the complete pipeline
- **🛡️ Production Ready**: Handles both development and production scenarios
- **📝 JSONB Storage**: Store complex item data as JSONB for flexible querying

---

## 📦 Installation

```bash
pip install scrapy-item-ingest
```

Or install from source:
```bash
git clone https://github.com/yourusername/scrapy_item_ingest.git
cd scrapy_item_ingest
pip install -e .
```

---

## 🛠️ Quick Start

### Basic Configuration

Add to your Scrapy project's `settings.py`:

```python
# Basic setup with auto table creation
ITEM_PIPELINES = {
    'scrapy_item_ingest.DbInsertPipeline': 300,
}

EXTENSIONS = {
    'scrapy_item_ingest.LoggingExtension': 500,
}

# Database configuration
DB_URL = 'postgresql://username:password@localhost:5432/database_name'

# Optional: Auto-create tables (default: True)
CREATE_TABLES = True

# Optional: Job identifier (uses spider name if not provided)
JOB_ID = 'my_crawl_job_001'
```

### Advanced Configuration

```python
# Development mode with custom job ID
CREATE_TABLES = True
JOB_ID = 'dev_crawl_20250721_001'

# Production mode with existing tables
CREATE_TABLES = False
JOB_ID = 'prod_job_001'

# Auto-fallback mode (no JOB_ID specified)
CREATE_TABLES = True
# JOB_ID will automatically use spider name

# Individual components
ITEM_PIPELINES = {
    'scrapy_item_ingest.ItemsPipeline': 300,        # Items only
    'scrapy_item_ingest.RequestsPipeline': 310,     # Requests only
}

EXTENSIONS = {
    'scrapy_item_ingest.LoggingExtension': 500,     # Logging only
}
```

---

## 📋 Database Schema

The system uses three predefined tables with consistent `job_id` based structure:

### Items Table (`job_items`)
```sql
CREATE TABLE job_items (
    id BIGSERIAL PRIMARY KEY,
    item JSONB NOT NULL,                  -- All scraped data as JSONB
    created_at TIMESTAMPTZ NOT NULL,      -- UTC timestamp
    job_id INTEGER NOT NULL               -- Job identifier
);
```

### Requests Table (`job_requests`)  
```sql
CREATE TABLE job_requests (
    id BIGSERIAL PRIMARY KEY,
    url VARCHAR(200) NOT NULL,            -- Request URL
    method VARCHAR(10) NOT NULL,          -- HTTP method (GET, POST, etc.)
    status_code INTEGER,                  -- Response status code
    response_time FLOAT,                  -- Response time in seconds
    fingerprint VARCHAR(255),             -- Unique request identifier
    parent_url VARCHAR(255),              -- URL of parent request
    created_at TIMESTAMPTZ NOT NULL,      -- UTC timestamp
    job_id INTEGER NOT NULL,              -- Job identifier
    parent_id BIGINT,                     -- Links to parent request
    FOREIGN KEY (parent_id) REFERENCES job_requests(id)
);
```

### Logs Table (`job_logs`)
```sql
CREATE TABLE job_logs (
    id BIGSERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL,              -- Job identifier
    type VARCHAR(50) NOT NULL,            -- Log type (INFO, ERROR, WARNING, etc.)
    message TEXT NOT NULL,                -- Log message
    created_at TIMESTAMPTZ NOT NULL       -- UTC timestamp
);
```

---

## 🎯 Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `DB_URL` | Required | PostgreSQL connection string |
| `CREATE_TABLES` | `True` | Auto-create tables if they don't exist |
| `JOB_ID` | `None` | Job identifier (uses spider name if not provided) |

**Table Management:**
- `CREATE_TABLES = True`: Automatically creates tables if they don't exist
- `CREATE_TABLES = False`: Uses existing tables (must already exist)
- `JOB_ID`: Used as identifier in both modes, falls back to spider name if not set

---

## 🔧 Usage Examples

### Example 1: Development with Custom Job ID
```python
# settings.py
CREATE_TABLES = True
JOB_ID = 'ecommerce_dev_20250721'
DB_URL = 'postgresql://user:pass@localhost:5432/dev_db'

# Result: Creates tables if needed, stores data using 'ecommerce_dev_20250721'
```

### Example 2: Development with Auto Spider Name
```python
# settings.py  
CREATE_TABLES = True
# No JOB_ID specified
DB_URL = 'postgresql://user:pass@localhost:5432/dev_db'

# Result: Creates tables if needed, stores data using spider name (e.g., 'my_spider')
```

### Example 3: Production with Job Tracking
```python
# settings.py
CREATE_TABLES = False
JOB_ID = 'prod_batch_001'
DB_URL = 'postgresql://user:pass@localhost:5432/prod_db'

# Result: Uses existing tables, stores data using 'prod_batch_001'
```

### Example 4: Production with Spider Names
```python
# settings.py
CREATE_TABLES = False
# No JOB_ID specified
DB_URL = 'postgresql://user:pass@localhost:5432/prod_db'

# Result: Uses existing tables, stores data using spider name
```

---

## 📊 Data Analysis Examples

### Query Parent-Child Request Relationships
```sql
-- Get request hierarchy
WITH RECURSIVE request_tree AS (
    SELECT id, url, parent_id, parent_url, 0 as level
    FROM job_requests WHERE parent_id IS NULL
    
    UNION ALL
    
    SELECT r.id, r.url, r.parent_id, r.parent_url, rt.level + 1
    FROM job_requests r
    JOIN request_tree rt ON r.parent_id = rt.id
)
SELECT * FROM request_tree ORDER BY level, id;
```

### Analyze Request Performance
```sql
-- Find slowest requests
SELECT url, AVG(response_time) as avg_response_time, COUNT(*) as request_count
FROM job_requests 
WHERE response_time IS NOT NULL
GROUP BY url
ORDER BY avg_response_time DESC
LIMIT 10;
```

### Extract Item Data
```sql
-- Query JSONB data
SELECT 
    item->>'title' as title,
    item->>'price' as price,
    item->>'category' as category,
    created_at
FROM job_items 
WHERE job_id = 'ecommerce_spider';
```

### Monitor Job Progress
```sql
-- Get job statistics
SELECT 
    job_id,
    COUNT(*) as total_items,
    MIN(created_at) as started_at,
    MAX(created_at) as last_item_at
FROM job_items 
GROUP BY job_id
ORDER BY started_at DESC;
```

---

## 🏗️ Architecture

### Modular Components

```
scrapy_item_ingest/
├── pipelines/          # Data processing pipelines
│   ├── items.py       # Item storage pipeline
│   ├── requests.py    # Request tracking pipeline
│   └── main.py        # Combined pipeline
├── extensions/         # Scrapy extensions
│   └── logging.py     # Event logging extension
├── database/          # Database operations
│   ├── connection.py  # Connection management
│   └── schema.py      # Schema management
├── config/            # Configuration utilities
│   └── settings.py    # Settings validation
└── utils/             # Utility functions
    ├── fingerprint.py # Request fingerprinting
    └── serialization.py # JSON serialization
```

### Individual Component Usage

```python
# Use only what you need
from scrapy_item_ingest import ItemsPipeline, LoggingExtension

ITEM_PIPELINES = {
    'scrapy_item_ingest.ItemsPipeline': 300,
}

EXTENSIONS = {
    'scrapy_item_ingest.LoggingExtension': 500,
}
```

---

## 🔍 Monitoring & Debugging

### Log Types Captured
- `INFO`: General information messages
- `ERROR`: Error events and exceptions  
- `WARNING`: Warning messages
- `DEBUG`: Debug information

### Request Tracking Features
- **Response Time Monitoring**: Track how long each request takes
- **Parent-Child Relationships**: See which requests led to others
- **Fingerprint Deduplication**: Unique identification of requests
- **Status Code Tracking**: Monitor request success/failure rates

### Item Processing
- **JSONB Storage**: Flexible schema for complex data structures
- **Timestamp Tracking**: Know exactly when items were processed
- **Job Isolation**: Group items by job or spider for easy analysis

---

## 🚀 Best Practices

### Development
```python
CREATE_TABLES = True     # Auto-create for quick setup
JOB_ID = None           # Use spider names for simplicity
```

### Production
```python  
CREATE_TABLES = False   # Use pre-created tables
JOB_ID = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}"  # Unique job IDs
```

### Performance Optimization
- Use connection pooling for high-throughput spiders
- Consider partitioning large tables by date or job_id
- Index frequently queried columns (job_id, created_at, url)
- Use JSONB indexing for complex item queries

### Recommended Indexes
```sql
-- Performance indexes
CREATE INDEX idx_job_items_job_id ON job_items(job_id);
CREATE INDEX idx_job_items_created_at ON job_items(created_at);
CREATE INDEX idx_job_requests_job_id ON job_requests(job_id);
CREATE INDEX idx_job_requests_url ON job_requests(url);
CREATE INDEX idx_job_requests_parent_id ON job_requests(parent_id);
CREATE INDEX idx_job_logs_job_id ON job_logs(job_id);
CREATE INDEX idx_job_logs_type ON job_logs(type);

-- JSONB indexes for item queries
CREATE INDEX idx_job_items_item_gin ON job_items USING GIN(item);
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built for the Scrapy ecosystem
- Inspired by production web scraping needs
- Designed for scalability and maintainability

---

**Happy Scraping! 🕷️✨**
