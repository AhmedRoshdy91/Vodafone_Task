# File Upload Web Service

A production-ready file upload web service built with FastAPI, demonstrating advanced software architecture patterns, polyglot persistence, and clean code principles.

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Development](#-development)
- [Testing](#-testing)
- [Performance](#-performance)
- [Troubleshooting](#-troubleshooting)

## 🎯 Overview

This project implements a comprehensive file upload service with the following capabilities:

- Upload and store text files
- Retrieve random lines from files with content negotiation
- Get the longest lines across all files or per file
- Support for multiple response formats (text/plain, JSON, XML)
- High-performance caching and query optimization
- Production-ready architecture with proper separation of concerns

## ✨ Features

### Core Functionality

✅ **File Upload**: Upload text files and store metadata and content  
✅ **Random Line**: Get one random line with content negotiation support  
✅ **Random Line Backwards**: Get random line reversed  
✅ **Longest 100 Lines**: Get 100 longest lines across all uploaded files  
✅ **Longest 20 Lines**: Get 20 longest lines from a specific file

### Content Negotiation

All line endpoints support multiple content types via `Accept` header:

- **text/plain**: Returns only the line text
- **application/json**: Returns `{"line": "..."}` (line text wrapped in JSON object)
- **application/xml**: Returns only the line text in XML format
- **application/\***: Returns full metadata (line, line_number, filename, most_frequent_letter)

**Note**: Use TypedDict for type-safe response formatting.

### Additional Features

- File management (list, get, delete)
- Health check endpoint
- Automatic API documentation (Swagger/ReDoc)
- Comprehensive error handling and validation
- Structured logging
- Connection pooling for all databases
- Context managers for resource management

### Key Optimizations

🚀 **Query Optimization**: Batch SQLite queries using `WHERE id IN (...)` for fetching multiple file metadata (N+1 query problem solved)

🎯 **Type Safety**: Full TypedDict implementation for response formatting with type hints throughout

🔧 **Configuration Management**: Application constants separated from environment variables for better maintainability

⚡ **Connection Pooling**: Optimized MongoDB (min: 1, max: 4) and Redis (max: 4) connection pools

🎨 **Strategy Pattern**: Clean content negotiation with dedicated formatters for each content type

## 🏗️ Architecture

### Technology Stack

| Component            | Technology | Purpose                                      |
| -------------------- | ---------- | -------------------------------------------- |
| **Web Framework**    | FastAPI    | Modern, high-performance async API framework |
| **File Metadata**    | SQLite     | Embedded database for file metadata          |
| **Line Content**     | MongoDB    | Document database for line content storage   |
| **Cache Layer**      | Redis      | High-performance caching for longest lines   |
| **Containerization** | Docker     | Service orchestration and deployment         |

### Design Patterns Implemented

1. **Repository Pattern**: Clean separation of data access logic from business logic
2. **Service Layer Pattern**: Business logic encapsulation and orchestration
3. **Strategy Pattern**: Content negotiation for different response formats (4 strategies: text, JSON, XML, metadata)
4. **Factory Pattern**: Dynamic response formatter creation based on Accept header
5. **Factory Method Pattern**: Entity creation from database rows
6. **Singleton Pattern**: Database connection management
7. **Dependency Injection**: FastAPI's built-in DI for loose coupling
8. **Context Manager Pattern**: Proper resource lifecycle management
9. **TypedDict Pattern**: Type-safe response formatting without Pydantic overhead

### Polyglot Persistence Strategy

```
┌──────────────┐      ┌─────────────┐      ┌──────────┐
│   SQLite     │      │   MongoDB   │      │  Redis   │
│              │      │             │      │          │
│ • File       │      │ • Line      │      │ • Global │
│   Metadata   │      │   Content   │      │   Cache  │
│ • Fast       │      │ • Analysis  │      │ • Per-   │
│   Queries    │      │   Data      │      │   File   │
└──────────────┘      └─────────────┘      └──────────┘
```

**Why Each Database?**

- **SQLite**: Fast, embedded, perfect for file metadata. Zero configuration.
- **MongoDB**: Flexible document model, excellent for storing line content with varying metadata.
- **Redis**: In-memory speed for caching longest lines (100x faster queries).

### Data Flow

```
┌─────────────┐
│ File Upload │
└──────┬──────┘
       │
       ├─────► SQLite (metadata: filename, size, line_count)
       │
       ├─────► Local FS (actual file content)
       │
       ├─────► MongoDB (each line + analysis)
       │
       └─────► Redis (cache longest lines)
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- 2GB RAM minimum
- 5GB disk space

### Installation & Running

1. **Clone/Navigate to the project directory**

```bash
cd /home/roshdy/Desktop/task
```

2. **Create environment file**

```bash
cp .env.example .env  # Or create .env manually
```

3. **Start all services**

```bash
docker-compose up -d
```

This will start:

- MongoDB (port 27017)
- Redis (port 6379)
- FastAPI Application (port 8000)

4. **Verify services are running**

```bash
docker-compose ps
```

Expected output:

```
NAME                STATUS          PORTS
fileservice_app     Up (healthy)    0.0.0.0:8000->8000/tcp
fileservice_mongodb Up              0.0.0.0:27017->27017/tcp
fileservice_redis   Up              0.0.0.0:6379->6379/tcp
```

5. **Access the API**

- **API Base URL**: http://localhost:8000
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

### Stop Services

```bash
# Stop services (preserve data)
docker-compose down

# Stop and remove all data
docker-compose down -v
```

## 📖 API Documentation

### Base URL

```
http://localhost:8000/api/v1
```

### Endpoints

#### 1. File Upload

Upload a text file and store it.

**Request:**

```bash
POST /api/v1/files/upload

curl -X POST http://localhost:8000/api/v1/files/upload \
  -F "file=@example.txt"
```

**Response:**

```json
{
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "example.txt",
  "lines_count": 1000,
  "file_size": 50000,
  "status": "success"
}
```

#### 2. Get Random Line

Get one random line from a file with content negotiation.

**Request:**

```bash
GET /api/v1/files/{file_id}/lines/random

# Text/Plain
curl -H "Accept: text/plain" \
  http://localhost:8000/api/v1/files/{file_id}/lines/random

# JSON (returns line only)
curl -H "Accept: application/json" \
  http://localhost:8000/api/v1/files/{file_id}/lines/random

# XML (returns line only)
curl -H "Accept: application/xml" \
  http://localhost:8000/api/v1/files/{file_id}/lines/random

# Wildcard (returns full metadata)
curl -H "Accept: application/*" \
  http://localhost:8000/api/v1/files/{file_id}/lines/random
```

**Response (JSON):**

```json
{
  "line": "This is a random line from the file"
}
```

**Response (XML):**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<line>This is a random line from the file</line>
```

**Response (application/\*):**

```json
{
  "line": "This is a random line from the file",
  "line_number": 42,
  "filename": "example.txt",
  "most_frequent_letter": "e"
}
```

#### 3. Get Random Line Backwards

Get random line reversed.

**Request:**

```bash
GET /api/v1/files/{file_id}/lines/random/backwards

curl -H "Accept: application/json" \
  http://localhost:8000/api/v1/files/{file_id}/lines/random/backwards
```

**Response (application/json):**

```json
{
  "line": "elif eht morf enil modnar a si sihT"
}
```

**Response (application/\*):**

```json
{
  "line": "elif eht morf enil modnar a si sihT",
  "line_number": 42,
  "filename": "example.txt",
  "most_frequent_letter": "e"
}
```

#### 4. Get Longest Lines (All Files)

Get the 100 longest lines across all uploaded files.

**Request:**

```bash
GET /api/v1/lines/longest?limit=100

curl http://localhost:8000/api/v1/lines/longest?limit=100
```

**Response:**

```json
{
  "lines": [
    {
      "line": "Very long line content...",
      "length": 850,
      "line_number": 42,
      "filename": "example.txt",
      "most_frequent_letter": "e",
      "frequency": 95
    }
  ],
  "count": 100
}
```

#### 5. Get Longest Lines (One File)

Get the 20 longest lines from a specific file.

**Request:**

```bash
GET /api/v1/files/{file_id}/lines/longest?limit=20

curl http://localhost:8000/api/v1/files/{file_id}/lines/longest?limit=20
```

#### 6. List Files

Get all uploaded files with pagination.

**Request:**

```bash
GET /api/v1/files?limit=100&offset=0

curl http://localhost:8000/api/v1/files
```

**Response:**

```json
{
  "files": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "example.txt",
      "original_filename": "example.txt",
      "file_size": 50000,
      "lines_count": 1000,
      "uploaded_at": "2025-10-20T10:30:00Z",
      "status": "active"
    }
  ],
  "count": 1
}
```

#### 7. Get File Details

Get details of a specific file.

**Request:**

```bash
GET /api/v1/files/{file_id}

curl http://localhost:8000/api/v1/files/{file_id}
```

#### 8. Delete File

Delete a file and all associated data.

**Request:**

```bash
DELETE /api/v1/files/{file_id}

curl -X DELETE http://localhost:8000/api/v1/files/{file_id}
```

**Response:**

```json
{
  "message": "File deleted successfully"
}
```

#### 9. Health Check

Check service health.

**Request:**

```bash
GET /api/v1/health

curl http://localhost:8000/api/v1/health
```

**Response:**

```json
{
  "status": "healthy",
  "databases": {
    "sqlite": "connected",
    "mongodb": "connected",
    "redis": "connected"
  }
}
```

## 🗂️ Project Structure

```
task/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application entry point
│   ├── config.py                    # Runtime configuration (Pydantic Settings)
│   ├── constants.py                 # Application constants (pool sizes, cache, file limits)
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py          # Dependency injection
│   │   └── routes.py                # API route handlers (fully typed)
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── sqlite.py                # SQLite connection manager
│   │   ├── mongodb.py               # MongoDB connection manager
│   │   └── redis_db.py              # Redis connection manager
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── entities.py              # Domain entities
│   │   └── schemas.py               # Pydantic models & TypedDicts
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── queries.py               # SQL query constants (batch queries)
│   │   ├── cache_queries.py         # Redis key constants
│   │   ├── file_repository.py       # File metadata operations (SQLite)
│   │   ├── line_repository.py       # Line content operations (MongoDB)
│   │   └── cache_repository.py      # Cache operations (Redis)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── file_service.py          # File business logic
│   │   └── line_service.py          # Line business logic
│   │
│   ├── strategies/
│   │   ├── __init__.py
│   │   ├── base.py                  # Response strategy interface
│   │   ├── plain_text_strategy.py   # text/plain formatter
│   │   ├── json_strategy.py         # application/json formatter (TypedDict)
│   │   ├── xml_strategy.py          # application/xml formatter
│   │   ├── metadata_strategy.py     # application/* formatter (TypedDict)
│   │   └── factory.py               # Strategy factory pattern
│   │
│   └── utils/
│       ├── __init__.py
│       ├── line_analyzer.py         # Line analysis utilities
│       ├── validators.py            # Input validation functions
│       └── file_processor.py        # File processing utilities
│
├── data/
│   └── fileservice.db               # SQLite database (auto-created)
│
├── uploads/                         # Uploaded files directory
│
├── mongo/
│   └── init-mongo.js                # MongoDB initialization script
│
├── docker-compose.yml               # Docker services configuration
├── Dockerfile                       # Application container definition
├── requirements.txt                 # Python dependencies
├── .env                             # Environment variables
├── .gitignore                       # Git ignore patterns
└── README.md                        # This file
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root for **runtime configuration**:

```env
# Application
APP_NAME=File Upload Service
DEBUG=True
ENVIRONMENT=development

# SQLite
SQLITE_DB_PATH=./data/fileservice.db

# MongoDB
MONGO_HOST=mongodb
MONGO_PORT=27017
MONGO_DB=fileservice
MONGO_USER=mongo
MONGO_PASSWORD=mongo123

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis123

# File Upload
UPLOAD_DIR=./uploads
```

### Application Constants

Application constants (pool sizes, cache settings, file limits) are defined in `app/constants.py`:

```python
class DatabasePoolSize:
    MONGODB_MAX_POOL_SIZE = 4
    MONGODB_MIN_POOL_SIZE = 1
    REDIS_MAX_CONNECTIONS = 4

class CacheDefaults:
    CACHE_TTL = 3600                      # 1 hour
    GLOBAL_LONGEST_CACHE_SIZE = 100       # Top 100 longest lines globally
    PER_FILE_LONGEST_CACHE_SIZE = 20      # Top 20 longest lines per file

class FileUploadDefaults:
    MAX_FILE_SIZE = 104857600             # 100MB in bytes
    ALLOWED_EXTENSIONS = ["txt", "csv", "log", "json", "xml"]
```

**Why separate constants from environment variables?**

- ✅ Type safety and IDE autocomplete
- ✅ No parsing errors (int, list, etc.)
- ✅ Better organization and maintainability
- ✅ Environment variables only for runtime configs (hosts, credentials)

## 💻 Development

### Local Development Setup

1. **Create virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Start databases (Docker)**

```bash
docker-compose up -d mongodb redis
```

4. **Update .env for local development**

```env
MONGO_HOST=localhost
REDIS_HOST=localhost
```

5. **Run the application**

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Code Quality Tools

```bash
# Format code
black app/

# Sort imports
isort app/

# Lint code
flake8 app/

# Type checking
mypy app/

# Security check
bandit -r app/
```

### Database Management

#### SQLite

```bash
# Open SQLite database
sqlite3 data/fileservice.db

# View tables
.tables

# View file metadata
SELECT * FROM files;

# Exit
.quit
```

#### MongoDB

```bash
# Connect to MongoDB
docker exec -it fileservice_mongodb mongosh -u mongo -p mongo123

# Use database
use fileservice

# View collections
show collections

# Count lines
db.lines.countDocuments()

# Find lines
db.lines.find().limit(5)

# Exit
exit
```

#### Redis

```bash
# Connect to Redis
docker exec -it fileservice_redis redis-cli -a redis123

# View all keys
KEYS *

# Get sorted set size
ZCARD longest:global

# View top 10 longest lines
ZREVRANGE longest:global 0 9 WITHSCORES

# Exit
exit
```

## 🧪 Testing

### Create Test Data

```bash
# Create a test file with 1000 lines of varying lengths
for i in {1..1000}; do
  length=$((50 + RANDOM % 200))
  line=$(head -c $length < /dev/urandom | base64 | tr -d '\n')
  echo "Line $i: $line" >> test.txt
done
```

### Manual API Testing

```bash
# 1. Upload a file
FILE_ID=$(curl -s -X POST http://localhost:8000/api/v1/files/upload \
  -F "file=@test.txt" | jq -r '.file_id')

echo "Uploaded file ID: $FILE_ID"

# 2. Get random line (JSON)
curl -H "Accept: application/json" \
  "http://localhost:8000/api/v1/files/$FILE_ID/lines/random" | jq

# 3. Get random line (XML)
curl -H "Accept: application/xml" \
  "http://localhost:8000/api/v1/files/$FILE_ID/lines/random"

# 4. Get random line (plain text)
curl -H "Accept: text/plain" \
  "http://localhost:8000/api/v1/files/$FILE_ID/lines/random"

# 5. Get random line with full metadata (application/*)
curl -H "Accept: application/*" \
  "http://localhost:8000/api/v1/files/$FILE_ID/lines/random" | jq

# 6. Get random line backwards
curl "http://localhost:8000/api/v1/files/$FILE_ID/lines/random/backwards" | jq

# 7. Get 100 longest lines (all files)
curl "http://localhost:8000/api/v1/lines/longest?limit=100" | jq '.count'

# 8. Get 20 longest lines for specific file
curl "http://localhost:8000/api/v1/files/$FILE_ID/lines/longest?limit=20" | jq '.count'

# 9. List all files
curl "http://localhost:8000/api/v1/files" | jq

# 10. Get file details
curl "http://localhost:8000/api/v1/files/$FILE_ID" | jq

# 11. Delete file
curl -X DELETE "http://localhost:8000/api/v1/files/$FILE_ID" | jq
```

### Performance Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils  # Ubuntu/Debian
# brew install httpd  # macOS

# Test upload endpoint (sequential)
ab -n 100 -c 1 -p test.txt -T "multipart/form-data" \
  http://localhost:8000/api/v1/files/upload

# Test random line endpoint (concurrent)
ab -n 1000 -c 10 \
  http://localhost:8000/api/v1/files/$FILE_ID/lines/random

# Test longest lines endpoint (with cache)
ab -n 1000 -c 10 \
  http://localhost:8000/api/v1/lines/longest?limit=100
```

## 📊 Performance

### Query Performance

| Operation             | Cold Cache | Hot Cache | Database Hit                           |
| --------------------- | ---------- | --------- | -------------------------------------- |
| Upload 10k lines      | ~2-3s      | N/A       | SQLite + MongoDB + Redis               |
| Get random line       | ~2-5ms     | ~1-2ms    | MongoDB (line content)                 |
| Get 100 longest (all) | ~10-20ms   | ~0.5-1ms  | Redis → MongoDB + **Single SQLite IN** |
| Get 20 longest (file) | ~5-10ms    | ~0.5-1ms  | Redis → MongoDB fallback               |
| List files            | ~1-2ms     | N/A       | SQLite                                 |

**Note**: Batch SQLite queries (`WHERE id IN (...)`) significantly reduced query time for fetching multiple file metadata from N queries to 1 query.

### Caching Strategy

**Global Cache** (Redis Sorted Set: `longest:global`)

- Stores top 100 longest lines across all files (configurable in `app/constants.py`)
- Key: line identifier (`file_id:line_number`)
- Score: line length

**Per-File Cache** (Redis Sorted Set: `longest:file:{file_id}`)

- Stores top 20 longest lines per file (configurable in `app/constants.py`)
- Key: line number
- Score: line length

**Line Content Cache** (Redis String: `line:{file_id}:{line_number}`)

- Caches full line content with metadata
- TTL: 1 hour (configurable)

### Scalability

**Current Architecture Limits:**

- SQLite: Good for < 100K files, < 100 concurrent users
- MongoDB: Horizontally scalable, handles millions of lines
- Redis: In-memory, can handle millions of cache entries

**To Scale Further:**

- Replace SQLite with PostgreSQL/MySQL for higher concurrency
- Add read replicas for MongoDB
- Use Redis Cluster for distributed caching
- Add load balancer for multiple app instances

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Check what's using the ports
lsof -i :8000   # FastAPI
lsof -i :27017  # MongoDB
lsof -i :6379   # Redis

# Kill the process or change ports in docker-compose.yml
```

#### 2. Database Connection Failed

```bash
# Check if services are running
docker-compose ps

# View logs
docker-compose logs mongodb
docker-compose logs redis

# Restart services
docker-compose restart mongodb redis
```

#### 3. Application Won't Start

```bash
# View application logs
docker-compose logs -f app

# Rebuild the container
docker-compose down
docker-compose build --no-cache app
docker-compose up -d
```

#### 4. File Upload Fails

```bash
# Check upload directory permissions
ls -la uploads/

# Create uploads directory if missing
mkdir -p uploads
chmod 755 uploads

# Check file size limits in app/constants.py
# FileUploadDefaults.MAX_FILE_SIZE = 104857600  # 100MB
# FileUploadDefaults.ALLOWED_EXTENSIONS = ["txt", "csv", "log", "json", "xml"]
```

#### 5. Redis Cache Not Working

```bash
# Connect to Redis and check
docker exec -it fileservice_redis redis-cli -a redis123

# Check if keys exist
KEYS *

# Check cache size
ZCARD longest:global

# Clear cache if needed
FLUSHDB
```

#### 6. Content Negotiation Not Working in Swagger

**Issue**: Swagger UI doesn't allow easy testing of different `Accept` headers.

**Solution**: Use cURL or Postman for testing content negotiation:

```bash
# Get JSON response
curl -H "Accept: application/json" \
  http://localhost:8000/api/v1/files/{file_id}/lines/random

# Get XML response
curl -H "Accept: application/xml" \
  http://localhost:8000/api/v1/files/{file_id}/lines/random

# Get text response
curl -H "Accept: text/plain" \
  http://localhost:8000/api/v1/files/{file_id}/lines/random

# Get full metadata
curl -H "Accept: application/*" \
  http://localhost:8000/api/v1/files/{file_id}/lines/random
```

**Note**: The `Accept` header parameter is hidden from Swagger schema (`include_in_schema=False`) but works correctly via cURL/Postman.

### Reset Everything

```bash
# Stop and remove all containers, volumes, and networks
docker-compose down -v

# Remove SQLite database
rm -f data/fileservice.db

# Remove uploaded files
rm -rf uploads/*

# Start fresh
docker-compose up -d
```

## 📝 API Response Codes

| Status Code | Description                                 |
| ----------- | ------------------------------------------- |
| 200         | Success                                     |
| 201         | Created (file uploaded)                     |
| 400         | Bad Request (invalid input)                 |
| 404         | Not Found (file/line doesn't exist)         |
| 406         | Not Acceptable (unsupported Accept header)  |
| 413         | Payload Too Large (file size exceeds limit) |
| 415         | Unsupported Media Type (not a text file)    |
| 500         | Internal Server Error                       |

## 🚀 Production Deployment

### Security Checklist

- [ ] Change all default passwords in `.env`
- [ ] Set `DEBUG=False` in production
- [ ] Configure CORS allowed origins
- [ ] Use HTTPS/TLS certificates
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerting
- [ ] Configure automatic backups
- [ ] Use secrets management (not .env files)
- [ ] Enable authentication and authorization

### Environment Variables for Production

```env
DEBUG=False
ENVIRONMENT=production

# Use strong passwords
MONGO_PASSWORD=<strong-random-password>
REDIS_PASSWORD=<strong-random-password>

# Configure CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Use PostgreSQL instead of SQLite for high concurrency
# (Requires code changes to use postgres.py instead of sqlite.py)
```

### Monitoring

```bash
# View logs
docker-compose logs -f

# Monitor resource usage
docker stats

# Check health endpoint
curl http://localhost:8000/api/v1/health
```

## 🎓 Design Principles

This project demonstrates:

1. **Clean Architecture**: Separation of concerns with clear layers
2. **SOLID Principles**: Single responsibility, dependency inversion, etc.
3. **DRY (Don't Repeat Yourself)**: Reusable components and utilities
4. **Dependency Injection**: Loose coupling between components
5. **Repository Pattern**: Database access abstraction
6. **Factory Pattern**: Object creation encapsulation
7. **Strategy Pattern**: Algorithm selection at runtime
8. **Context Managers**: Proper resource lifecycle management

## 📚 Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **MongoDB Documentation**: https://docs.mongodb.com
- **Redis Documentation**: https://redis.io/docs
- **Docker Documentation**: https://docs.docker.com

## 📄 License

This project is created for a Vodafone code challenge.

## 👨‍💻 Author

Ahmed Roshdy
---

**Interactive API Documentation**: http://localhost:8000/docs  
**Alternative Documentation**: http://localhost:8000/redoc  
**Health Check**: http://localhost:8000/api/v1/health
