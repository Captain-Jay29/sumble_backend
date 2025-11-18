# Sumble Advanced Query API

A FastAPI-based REST API that supports advanced boolean queries on job data with proper SQL JOIN logic for normalized database schemas.

## Features

- **Advanced Boolean Logic**: Support for AND, OR, and NOT operators
- **Nested Queries**: Handles arbitrarily complex nested boolean expressions
- **Dynamic JOIN Building**: Only JOINs tables that are actually needed for the query
- **Searchable Fields**: 
  - `organization` - Company name search
  - `technology` - Technology/stack search
  - `job_function` - Job role search
- **Fast Performance**: Async database connections with connection pooling
- **Production Ready**: Proper error handling, SQL injection prevention, Docker deployment

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Port 8000 and 5432 available
- Python 3.12+ (for testing)

### Run the Application

```bash
# Using Makefile (recommended)
make up

# Or manually with Docker Compose
docker compose up --build -d

# API will be available at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

See [QUICK_START.md](QUICK_START.md) for detailed setup instructions.

### Test the API

**Option 1: Web Interface (Recommended)**

A minimalist web UI is available for testing queries visually:

```bash
# Open directly in browser
open frontend/index.html

# Or serve with Python for better compatibility
cd frontend && python3 -m http.server 3000
# Then visit: http://localhost:3000
```

See [frontend/README.md](frontend/README.md) for details.

**Option 2: Command Line (curl)**

See `curl_examples.md` for detailed examples. Quick test:

```bash
# Query 1: Jobs at Apple using .NET
curl -X POST "http://localhost:8000/api/v1/jobs/search" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "operator",
    "operator": "AND",
    "children": [
      {"type": "condition", "condition": {"field": "organization", "value": "apple"}},
      {"type": "condition", "condition": {"field": "technology", "value": ".net"}}
    ]
  }'
```

## Project Structure

```
sumble/
├── app/                  # Main application code
├── tests/                # Test suite (23 test cases)
├── scripts/              # Utility scripts
├── reports/              # Generated test reports
├── docs/                 # Documentation
├── docker-compose.yml    # Docker services (db + api)
├── Dockerfile           # API container
├── requirements.txt     # Python dependencies
├── curl_examples.md     # Example API calls
├── README.md           # This file
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed directory layout.

## API Documentation

### POST /api/v1/jobs/search

Search for jobs using boolean queries.

**Parameters:**
- `query` (body, required): QueryNode object defining the search criteria
- `limit` (query, optional): Maximum results to return (default: 10)

**Response:**
```json
{
  "status": "success",
  "count": 3,
  "jobs": [
    {"id": 184916, "datetime_pulled": "2022-09-18T13:48:34.502481Z"},
    ...
  ]
}
```

### GET /api/v1/health

Health check endpoint.

**Response:**
```json
{"status": "healthy"}
```

## Query Model

The API uses a tree-based query model that supports nested boolean logic:

```typescript
{
  "type": "operator" | "condition",
  "operator": "AND" | "OR" | "NOT",  // if type is "operator"
  "condition": {                      // if type is "condition"
    "field": "organization" | "technology" | "job_function",
    "value": "search string"
  },
  "children": [QueryNode, ...]        // if type is "operator"
}
```

## Architecture

### Database Schema

The database uses a normalized schema with junction tables for many-to-many relationships:

- **job_posts** - Main job posting table
- **organizations** - Company lookup table (linked via `organization_id`)
- **tech** - Technology lookup table
- **job_functions** - Job function lookup table
- **job_posts_tech** - Junction table linking jobs to technologies
- **job_posts_job_functions** - Junction table linking jobs to job functions

### Query Building Strategy

1. **Field Collection**: Recursively scan the query tree to determine which fields are needed
2. **Dynamic JOINs**: Only JOIN tables that are actually required for the query
3. **Parameter Tracking**: Use proper parameter offset tracking to handle nested queries correctly
4. **SQL Generation**: Build parameterized SQL queries with `$1, $2, ...` placeholders
5. **Execution**: Run async queries with connection pooling for performance

### Key Design Decisions

- **asyncpg over ORM**: Direct database driver for better performance
- **Tree-based queries**: Clean representation of nested boolean logic
- **Parameter offset tracking**: Prevents SQL parameter numbering conflicts in nested queries
- **DISTINCT results**: Necessary due to many-to-many JOINs creating duplicate rows
- **ILIKE searches**: Case-insensitive partial matching for better UX

## Technology Stack

- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn 0.24.0 with asyncio
- **Database Driver**: asyncpg 0.29.0
- **Validation**: Pydantic 2.5.0
- **Database**: PostgreSQL 17
- **Deployment**: Docker + Docker Compose

## Development

### Local Development (without Docker)

```bash
# Set up Python environment
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
export PGHOST=localhost
export PGPORT=5432
export PGUSER=postgres
export PGPASSWORD=supersecretpassword
export PGDATABASE=sumble_data

# Run the API
uvicorn app.main:app --reload
```

### Run Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run comprehensive test suite
python tests/test_queries.py

# Visualize performance metrics
python scripts/visualize_results.py
```

### View Logs

```bash
# API logs
docker compose logs api -f

# Database logs
docker compose logs db -f
```

### Stop Services

```bash
docker compose down
```

## Testing

Both required queries have been tested and verified:

**Query 1**: `organization: apple AND tech: .net`
- Result: 3 jobs found
- Response time: < 1 second

**Query 2**: `NOT organization: apple AND (job_function: statistician OR tech: psql)`
- Result: 3 jobs found  
- Response time: < 2 seconds

## Interactive Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive API documentation and testing interfaces.

## Error Handling

The API properly handles:
- Invalid query structures (400 Bad Request)
- Database connection errors (500 Internal Server Error)
- Malformed JSON (422 Unprocessable Entity)
- SQL injection attempts (parameterized queries prevent this)

## Performance

- Connection pooling (10-20 connections)
- Async I/O for concurrent requests
- Dynamic JOINs reduce unnecessary database work
- Indexed foreign keys for fast joins
- Response times well under 30 seconds for complex queries

## Future Enhancements

Potential improvements for production:
- Add query result caching (Redis)
- Implement pagination for large result sets
- Add query complexity limits to prevent expensive operations
- Add authentication/authorization
- Add rate limiting
- Add metrics and monitoring (Prometheus/Grafana)
- Use EXISTS subqueries instead of JOINs to avoid DISTINCT overhead
- Add full-text search capabilities

## License

This is a take-home assessment project for Sumble.
