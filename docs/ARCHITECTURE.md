# Sumble Advanced Query API - Architecture & Process Flow

## Port Configuration

| Service | Container Port | Host Port | URL |
|---------|---------------|-----------|-----|
| **FastAPI Server** | 8000 | 8000 | http://localhost:8000 |
| **PostgreSQL Database** | 5432 | 5432 | localhost:5432 |

### Service Details

**API Server (sumble-api)**
- **Internal Port**: 8000
- **External Port**: 8000
- **Access**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

**Database Server (sumble-db)**
- **Internal Port**: 5432
- **External Port**: 5432
- **Connection String**: `postgresql://postgres:supersecretpassword@localhost:5432/sumble_data`
- **Direct Access**: pgAdmin4, psql, or any Postgres client

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                 │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 │ HTTP Request (JSON)
                                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    API SERVER (Port 8000)                            │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  FastAPI Application (app/main.py)                             │ │
│  │  ├── Lifespan Management (DB connection pooling)               │ │
│  │  ├── CORS Middleware                                           │ │
│  │  └── API Router (/api/v1)                                      │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                 │                                    │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  API Endpoints (app/api.py)                                    │ │
│  │  ├── POST /api/v1/jobs/search  (main query endpoint)          │ │
│  │  └── GET  /api/v1/health       (health check)                 │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                 │                                    │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  Request Validation (app/models.py)                            │ │
│  │  └── Pydantic Models: QueryNode, Condition, Operators         │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                 │                                    │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  Query Builder (app/query_builder.py)                          │ │
│  │  ├── Collect required fields from query tree                   │ │
│  │  ├── Build dynamic JOINs (only add needed tables)             │ │
│  │  ├── Generate WHERE clause with parameter tracking            │ │
│  │  └── Construct final SQL with DISTINCT + LIMIT                │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                 │                                    │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  Database Layer (app/database.py)                              │ │
│  │  ├── AsyncPG Connection Pool (10-20 connections)               │ │
│  │  └── Execute parameterized queries ($1, $2, ...)              │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 │ SQL Query (asyncpg)
                                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                  DATABASE SERVER (Port 5432)                         │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  PostgreSQL 17 (sumble_data)                                   │ │
│  │                                                                 │ │
│  │  Main Tables:                                                  │ │
│  │  ├── job_posts          (89,397 jobs)                         │ │
│  │  ├── organizations      (companies)                           │ │
│  │  ├── tech               (technologies)                        │ │
│  │  └── job_functions      (job roles)                           │ │
│  │                                                                 │ │
│  │  Junction Tables (Many-to-Many):                              │ │
│  │  ├── job_posts_tech              (job ↔ technology)           │ │
│  │  └── job_posts_job_functions     (job ↔ function)            │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 │ Results
                                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     EXTERNAL TOOLS                                   │
│  ├── pgAdmin4 (GUI for database)       → Port 5432                  │
│  ├── psql (CLI for database)           → Port 5432                  │
│  └── curl/httpx (API testing)          → Port 8000                  │
└─────────────────────────────────────────────────────────────────────┘
```

## Request Flow Diagram

### Query Processing Flow

```
1. CLIENT REQUEST
   │
   │  POST http://localhost:8000/api/v1/jobs/search
   │  Body: { "type": "operator", "operator": "AND", ... }
   │
   ↓
2. FASTAPI RECEIVES REQUEST
   │
   ├─→ Validate JSON against Pydantic models
   │   ├─ QueryNode structure
   │   ├─ Operator types (AND/OR/NOT)
   │   └─ Field types (organization/technology/job_function)
   │
   ↓
3. QUERY BUILDER PROCESSES
   │
   ├─→ Analyze query tree
   │   └─ Collect required fields: {organization, technology}
   │
   ├─→ Build base SQL with dynamic JOINs
   │   └─ SELECT DISTINCT jp.id, jp.datetime_pulled
   │       FROM job_posts jp
   │       INNER JOIN organizations o ON jp.organization_id = o.id
   │       INNER JOIN job_posts_tech jpt ON jp.id = jpt.job_post_id
   │       INNER JOIN tech t ON jpt.tech_id = t.id
   │
   ├─→ Build WHERE clause with parameter tracking
   │   └─ WHERE o.name ILIKE $1 AND t.name ILIKE $2
   │       params: ['%apple%', '%.net%']
   │
   └─→ Add LIMIT
       └─ LIMIT 10
   │
   ↓
4. DATABASE EXECUTES QUERY
   │
   ├─→ Parse SQL
   ├─→ Optimize query plan
   ├─→ Execute JOINs
   ├─→ Apply WHERE filters
   ├─→ DISTINCT deduplication
   └─→ LIMIT results
   │
   ↓
5. RESULTS RETURNED
   │
   ├─→ Database → asyncpg → FastAPI
   │
   └─→ Format response:
       {
         "status": "success",
         "count": 3,
         "jobs": [
           {"id": 184916, "datetime_pulled": "2022-09-18..."},
           ...
         ]
       }
   │
   ↓
6. CLIENT RECEIVES RESPONSE
   └─→ HTTP 200 OK with JSON payload
```

## Data Flow for Complex Query

**Example**: `NOT organization: apple AND (job_function: statistician OR tech: psql)`

```
Query Tree:
    AND
    ├── NOT
    │   └── organization: apple
    └── OR
        ├── job_function: statistician
        └── tech: psql

↓ Query Builder Analysis ↓

Required JOINs:
├── organizations (for NOT apple)
├── job_posts_tech → tech (for psql)
└── job_posts_job_functions → job_functions (for statistician)

↓ SQL Generation ↓

SELECT DISTINCT jp.id, jp.datetime_pulled
FROM job_posts jp
INNER JOIN organizations o ON jp.organization_id = o.id
INNER JOIN job_posts_tech jpt ON jp.id = jpt.job_post_id
INNER JOIN tech t ON jpt.tech_id = t.id
INNER JOIN job_posts_job_functions jpjf ON jp.id = jpjf.job_post_id
INNER JOIN job_functions jf ON jpjf.job_function_id = jf.id
WHERE (NOT (o.name ILIKE $1)) AND ((jf.name ILIKE $2) OR (t.name ILIKE $3))
LIMIT 10

Parameters: ['%apple%', '%statistician%', '%psql%']

↓ Database Execution ↓

1. Scan job_posts (89,397 rows)
2. JOIN with organizations (filter NOT apple)
3. JOIN with junction tables
4. JOIN with tech and job_functions
5. Apply WHERE clause
6. DISTINCT to remove duplicates from many-to-many JOINs
7. LIMIT to 10 results

↓ Return Results ↓

3 jobs found, returned as JSON
```

## Component Interaction

```
┌──────────────┐     HTTP/JSON      ┌──────────────┐
│              │ ←─────────────────→ │              │
│   Client     │                     │  FastAPI     │
│  (curl/web)  │                     │   Server     │
│              │                     │  :8000       │
└──────────────┘                     └──────┬───────┘
                                            │
                                            │ SQL
                                            │ (asyncpg)
                                            ↓
                                     ┌──────────────┐
                                     │  PostgreSQL  │
                                     │  Database    │
                                     │  :5432       │
                                     └──────────────┘
                                            ↑
                                            │ SQL
                                            │ (pgAdmin4)
                                            │
                                     ┌──────────────┐
                                     │   pgAdmin4   │
                                     │  (GUI Tool)  │
                                     └──────────────┘
```

## Docker Network

```
Docker Network: sumble_default
│
├── Container: sumble-db
│   ├── Internal: db:5432
│   └── External: localhost:5432
│       └── Accessible from host machine
│
└── Container: sumble-api
    ├── Internal: api:8000
    ├── External: localhost:8000
    │   └── Accessible from host machine
    └── Environment Variables:
        ├── PGHOST=db (internal Docker DNS)
        ├── PGPORT=5432
        ├── PGUSER=postgres
        ├── PGPASSWORD=supersecretpassword
        └── PGDATABASE=sumble_data
```

## Connection Examples

### From Host Machine (Your Computer)

```bash
# Access API
curl http://localhost:8000/api/v1/health

# Access Database (pgAdmin4)
Host: localhost
Port: 5432

# Access Database (psql)
psql -h localhost -p 5432 -U postgres -d sumble_data
```

### From API Container to Database

```python
# API connects to database using internal Docker DNS
host='db'  # Not 'localhost'!
port=5432
```

### From Test Suite (Your Computer)

```bash
# Tests hit the API
python tests/test_queries.py
# → Connects to http://localhost:8000
#   → API connects to db:5432 internally
```

## Performance Characteristics

| Layer | Average Latency | Notes |
|-------|----------------|-------|
| **Client → API** | < 1ms | Local network |
| **API Processing** | 5-10ms | Pydantic validation + query building |
| **Database Query** | 100-200ms | Complex JOINs across 5 tables |
| **Total Response** | 150-250ms | Average query time |

## Security Features

1. **Parameterized Queries**: SQL injection prevention via `$1, $2, ...`
2. **Connection Pooling**: Limit concurrent DB connections (10-20)
3. **CORS Middleware**: Control cross-origin requests
4. **Input Validation**: Pydantic models validate all inputs
5. **Docker Isolation**: Services run in isolated containers

## Key Design Decisions

1. **Async All the Way**: FastAPI + asyncpg for concurrent request handling
2. **Dynamic JOINs**: Only add tables needed for specific query
3. **Parameter Tracking**: Prevents conflicts in nested queries
4. **DISTINCT**: Handle many-to-many duplicate results
5. **Connection Pool**: Reuse DB connections efficiently

---

**Summary:**
- **API Server**: Port 8000 (FastAPI)
- **Database**: Port 5432 (PostgreSQL)
- **Both accessible from host** via `localhost`
- **API → DB communication** via Docker internal network (`db:5432`)

