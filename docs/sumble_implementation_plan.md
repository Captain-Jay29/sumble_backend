# Sumble Advanced Query API - Implementation Plan

## Project Overview
Build an API that supports advanced boolean queries on job data for Sumble's backend engineering assessment. This implementation uses Python with FastAPI to create a clean, efficient solution.

## Database Schema Understanding

The database consists of:
- **job_posts**: Main table with job postings
- **organizations**: Company lookup table (linked via organization_id)
- **tech**: Technology lookup table
- **job_functions**: Job function lookup table
- **job_posts_tech**: Junction table linking jobs to technologies
- **job_posts_job_functions**: Junction table linking jobs to job functions

## Core Requirements
1. **Advanced Query API**: Build an API that supports complex boolean queries on job data
2. **Boolean Logic Support**: Implement AND, OR, and NOT operators
3. **Searchable Fields**: 
   - `technology` → Query against `tech.name` via junction table
   - `job_function` → Query against `job_functions.name` via junction table
   - `organization` → Query against `organizations.name` via foreign key
4. **Performance**: Must handle complex queries in < 30 seconds
5. **Deployment**: Must be containerized and runnable via Docker Compose

## Technology Stack
- **Framework**: FastAPI (async support, automatic API documentation)
- **Database Driver**: asyncpg (for async PostgreSQL connections)
- **Validation**: Pydantic (built into FastAPI)
- **Server**: Uvicorn
- **Optional**: SQLAlchemy Core for query building (if complex SQL gets unwieldy)

## Project Structure (Simplified)
```
sumble-query-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py                # Configuration
│   ├── models.py                # Pydantic models for requests/responses
│   ├── query_builder.py         # SQL query construction logic
│   ├── database.py              # Database connection and queries
│   └── api.py                   # API endpoints
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── README.md
└── curl_examples.md             # Required curl examples
```

## Implementation Steps

### Step 1: Database Connection (10 mins)

Simple async database connection:

```python
# app/database.py
import asyncpg
from typing import List, Dict, Any
import os

class Database:
    def __init__(self):
        self.pool = None
        
    async def connect(self):
        self.pool = await asyncpg.create_pool(
            host=os.getenv('PGHOST', 'localhost'),
            port=os.getenv('PGPORT', 5432),
            user=os.getenv('PGUSER', 'postgres'),
            password=os.getenv('PGPASSWORD', 'supersecretpassword'),
            database=os.getenv('PGDATABASE', 'sumble_data'),
            min_size=10,
            max_size=20
        )
    
    async def disconnect(self):
        if self.pool:
            await self.pool.close()
    
    async def execute_query(self, query: str, *args) -> List[Dict[str, Any]]:
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(query, *args)
            return [dict(row) for row in rows]

# Global database instance
db = Database()
```

### Step 2: Query Model Design

Create Pydantic models for query validation:

```python
# app/models/query.py
from pydantic import BaseModel, Field
from typing import Union, List, Literal, Optional
from enum import Enum

class FieldType(str, Enum):
    TECHNOLOGY = "technology"
    JOB_FUNCTION = "job_function"
    ORGANIZATION = "organization"

class Condition(BaseModel):
    field: FieldType
    value: str

class LogicalOperator(str, Enum):
    AND = "AND"
    OR = "OR"
    NOT = "NOT"

class QueryNode(BaseModel):
    type: Literal["condition", "operator"]
    operator: Optional[LogicalOperator] = None
    condition: Optional[Condition] = None
    children: Optional[List['QueryNode']] = None

    class Config:
        schema_extra = {
            "example": {
                "type": "operator",
                "operator": "AND",
                "children": [
                    {
                        "type": "condition",
                        "condition": {
                            "field": "organization",
                            "value": "apple"
                        }
                    },
                    {
                        "type": "condition",
                        "condition": {
                            "field": "technology",
                            "value": ".net"
                        }
                    }
                ]
            }
        }

QueryNode.model_rebuild()  # Required for self-referential models
```

### Step 3: Query Builder

Implement SQL query builder using the actual database schema:

```python
# app/query_builder.py
from typing import Tuple, List, Any, Set
from app.models import QueryNode, LogicalOperator, FieldType

class QueryBuilder:
    def build_query(self, node: QueryNode, limit: int = 10) -> Tuple[str, List[Any]]:
        """
        Build complete SQL query with JOINs and WHERE clause
        """
        # Collect all field types needed for JOINs
        required_joins = self._collect_required_fields(node)
        
        # Build base query with necessary JOINs
        base_query = self._build_base_query(required_joins)
        
        # Build WHERE clause
        where_clause, params, _ = self._build_where_clause(node)
        
        # Combine into final query
        query = f"{base_query} WHERE {where_clause} LIMIT {limit}"
        
        return query, params
    
    def _collect_required_fields(self, node: QueryNode) -> Set[FieldType]:
        """Recursively collect all field types that need JOINs"""
        fields = set()
        
        if node.type == "condition":
            fields.add(node.condition.field)
        elif node.type == "operator" and node.children:
            for child in node.children:
                fields.update(self._collect_required_fields(child))
        
        return fields
    
    def _build_base_query(self, required_fields: Set[FieldType]) -> str:
        """Build SELECT with necessary JOINs based on required fields"""
        query_parts = [
            "SELECT DISTINCT jp.id, jp.datetime_pulled",
            "FROM job_posts jp"
        ]
        
        if FieldType.ORGANIZATION in required_fields:
            query_parts.append("INNER JOIN organizations o ON jp.organization_id = o.id")
        
        if FieldType.TECHNOLOGY in required_fields:
            query_parts.append("INNER JOIN job_posts_tech jpt ON jp.id = jpt.job_post_id")
            query_parts.append("INNER JOIN tech t ON jpt.tech_id = t.id")
        
        if FieldType.JOB_FUNCTION in required_fields:
            query_parts.append("INNER JOIN job_posts_job_functions jpjf ON jp.id = jpjf.job_post_id")
            query_parts.append("INNER JOIN job_functions jf ON jpjf.job_function_id = jf.id")
        
        return " ".join(query_parts)
    
    def _build_where_clause(self, node: QueryNode, param_offset: int = 0) -> Tuple[str, List[Any], int]:
        """Recursively build WHERE clause from query tree. Returns (clause, params, next_offset)"""
        if node.type == "condition":
            return self._build_condition(node.condition, param_offset)
        elif node.type == "operator":
            return self._build_operator(node, param_offset)
        else:
            raise ValueError(f"Unknown node type: {node.type}")
    
    def _build_condition(self, condition, param_offset: int) -> Tuple[str, List[Any], int]:
        """Build SQL condition for a single field"""
        # Map fields to actual database columns
        field_mapping = {
            FieldType.TECHNOLOGY: "t.name",
            FieldType.JOB_FUNCTION: "jf.name", 
            FieldType.ORGANIZATION: "o.name"
        }
        
        column = field_mapping[condition.field]
        # Use ILIKE for case-insensitive search with proper param numbering
        return f"{column} ILIKE ${param_offset + 1}", [f"%{condition.value}%"], param_offset + 1
    
    def _build_operator(self, node: QueryNode, param_offset: int) -> Tuple[str, List[Any], int]:
        """Build SQL for logical operators with proper parameter tracking"""
        if node.operator == LogicalOperator.NOT:
            sub_clause, params, next_offset = self._build_where_clause(node.children[0], param_offset)
            return f"NOT ({sub_clause})", params, next_offset
        
        # For AND/OR operators
        clauses = []
        all_params = []
        current_offset = param_offset
        
        for child in node.children:
            sub_clause, params, current_offset = self._build_where_clause(child, current_offset)
            clauses.append(f"({sub_clause})")
            all_params.extend(params)
        
        operator = " AND " if node.operator == LogicalOperator.AND else " OR "
        return operator.join(clauses), all_params, current_offset
```

### Step 4: API Endpoints

Create the FastAPI application and endpoints:

```python
# app/api.py
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.models import QueryNode
from app.query_builder import QueryBuilder
from app.database import db

router = APIRouter()

@router.post("/jobs/search")
async def search_jobs(query: QueryNode, limit: int = 10) -> Dict[str, Any]:
    """
    Search for jobs using advanced boolean queries.
    
    Example query structure:
    {
        "type": "operator",
        "operator": "AND",
        "children": [
            {"type": "condition", "condition": {"field": "organization", "value": "apple"}},
            {"type": "condition", "condition": {"field": "technology", "value": ".net"}}
        ]
    }
    """
    try:
        builder = QueryBuilder()
        sql_query, params = builder.build_query(query, limit)
        
        # Execute query
        jobs = await db.execute_query(sql_query, *params)
        
        return {
            "status": "success",
            "count": len(jobs),
            "jobs": jobs
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error: {e}")  # Log for debugging
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
```

### Step 5: Main Application

Create the FastAPI application:

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api import router
from app.database import db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db.connect()
    yield
    # Shutdown
    await db.disconnect()

app = FastAPI(
    title="Sumble Advanced Query API",
    description="API for advanced job searching with boolean queries",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Step 6: Configuration

Simple configuration file:

```python
# app/config.py
import os

class Config:
    PGHOST = os.getenv("PGHOST", "localhost")
    PGPORT = os.getenv("PGPORT", "5432")
    PGUSER = os.getenv("PGUSER", "postgres")
    PGPASSWORD = os.getenv("PGPASSWORD", "supersecretpassword")
    PGDATABASE = os.getenv("PGDATABASE", "sumble_data")
```

## Docker Configuration

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  db:
    image: nzsne8pttnh8wrpu/p2ckp9ddret2arc2
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 1s
      timeout: 5s
      retries: 5
    ports:
      - 5432:5432
    environment:
      POSTGRES_PASSWORD: supersecretpassword

  api:
    build: .
    depends_on:
      db:
        condition: service_healthy
    ports:
      - 8000:8000
    environment:
      - PGHOST=db
      - PGPORT=5432
      - PGUSER=postgres
      - PGPASSWORD=supersecretpassword
      - PGDATABASE=sumble_data
      - DEBUG=false
    volumes:
      - ./app:/app/app  # For development hot reload
```

### requirements.txt
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
asyncpg==0.29.0
pydantic==2.5.0
```

## CURL Examples

### Query 1: organization: apple AND tech: .net
```bash
curl -X POST "http://localhost:8000/api/v1/jobs/search" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "operator",
    "operator": "AND",
    "children": [
      {
        "type": "condition",
        "condition": {
          "field": "organization",
          "value": "apple"
        }
      },
      {
        "type": "condition",
        "condition": {
          "field": "technology",
          "value": ".net"
        }
      }
    ]
  }'
```

### Query 2: NOT organization: apple AND (job_function: statistician OR tech: psql)
```bash
curl -X POST "http://localhost:8000/api/v1/jobs/search" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "operator",
    "operator": "AND",
    "children": [
      {
        "type": "operator",
        "operator": "NOT",
        "children": [
          {
            "type": "condition",
            "condition": {
              "field": "organization",
              "value": "apple"
            }
          }
        ]
      },
      {
        "type": "operator",
        "operator": "OR",
        "children": [
          {
            "type": "condition",
            "condition": {
              "field": "job_function",
              "value": "statistician"
            }
          },
          {
            "type": "condition",
            "condition": {
              "field": "technology",
              "value": "psql"
            }
          }
        ]
      }
    ]
  }'
```

## Development Workflow

### 1. Quick Database Verification (5 mins)
```python
# Quick script to verify our understanding of the schema
import asyncio
import asyncpg

async def verify_schema():
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='postgres',
        password='supersecretpassword',
        database='sumble_data'
    )
    
    # Test a simple query to verify the schema
    test_query = """
        SELECT COUNT(DISTINCT jp.id) as count
        FROM job_posts jp
        INNER JOIN organizations o ON jp.organization_id = o.id
        WHERE o.name ILIKE '%apple%'
    """
    
    result = await conn.fetchone(test_query)
    print(f"Jobs at Apple: {result['count']}")
    
    await conn.close()

asyncio.run(verify_schema())
```

### 2. Core Implementation (1.5 hours)
- Create models.py with Pydantic models
- Implement query_builder.py with JOIN logic
- Set up database.py with connection pooling
- Create api.py with endpoints
- Wire everything in main.py

### 3. Testing (30 mins)
- Test both required queries manually
- Verify response times are under 30 seconds
- Test edge cases (empty results, invalid queries)
- Test nested boolean logic

### 4. Dockerization (15 mins)
- Create Dockerfile
- Set up docker-compose.yml
- Test with `docker compose up --build`
- Verify both queries work in containerized environment

### 5. Documentation (10 mins)
- Create curl_examples.md with both required queries
- Write brief README
- Double-check all requirements are met

## Testing the Application

1. **Start the services:**
   ```bash
   docker compose up --build
   ```

2. **Check API documentation:**
   Navigate to `http://localhost:8000/docs` for interactive Swagger UI

3. **Run the test queries:**
   Execute the provided curl commands

4. **Monitor logs:**
   ```bash
   docker compose logs -f api
   ```

## Key Design Decisions

1. **Direct asyncpg usage**: Skip the ORM overhead for better performance
2. **Tree-based Query Structure**: Clean representation of nested boolean logic
3. **Dynamic JOIN building**: Only JOIN tables that are actually needed for the query
4. **Connection pooling**: Built-in asyncpg pooling for concurrent requests
5. **Parameterized queries**: Prevent SQL injection with numbered parameters ($1, $2, etc.)
6. **Simple architecture**: Minimal layers for a 3-hour project - focus on working code

## Why This Approach?

- **Performance**: Direct SQL with proper JOINs will be fast
- **Simplicity**: No over-engineering with unnecessary abstraction layers
- **Maintainability**: Clear separation between query building and API logic
- **Time-efficient**: Can be implemented within the 3-hour constraint
- **Production-ready**: Handles edge cases, SQL injection prevention, proper error handling

## Submission Checklist

- [ ] Both required queries execute successfully
- [ ] Response times are under 30 seconds
- [ ] Application runs with `docker compose up --build`
- [ ] CURL examples documented for both queries
- [ ] All files included in ZIP:
  - [ ] app/ directory with Python code
  - [ ] docker-compose.yml
  - [ ] Dockerfile
  - [ ] requirements.txt
  - [ ] curl_examples.md or README with examples
- [ ] Submit via: https://forms.gle/AkcyVcfYNFzm7hy78

## Quick Tips for Success

1. **Start simple**: Get a basic query working first, then add complexity
2. **Test early**: Verify your JOINs return correct data before building the API
3. **Use FastAPI docs**: Navigate to http://localhost:8000/docs to test your API
4. **Handle edge cases**: Empty results, malformed queries, etc.
5. **Keep it clean**: This is a take-home test - code quality matters

Good luck with your implementation!