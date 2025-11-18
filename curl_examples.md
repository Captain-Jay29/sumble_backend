# Sumble API - cURL Examples

## Required Submission Queries

These are the two queries required by the project specifications.

### Query 1: organization: apple AND tech: .net

**Expected Result**: Jobs at Apple using .NET technology (< 30 seconds)

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

**Expected Response**:
```json
{
  "status": "success",
  "count": 3,
  "jobs": [
    {"id": 184916, "datetime_pulled": "2022-09-18T13:48:34.502481Z"},
    {"id": 491622, "datetime_pulled": "2022-09-18T13:48:48.660711Z"},
    {"id": 553333, "datetime_pulled": "2022-11-07T12:08:51.573364Z"}
  ]
}
```

---

### Query 2: NOT organization: apple AND (job_function: statistician OR tech: psql)

**Expected Result**: Jobs NOT at Apple, with either Statistician role OR PSQL technology

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

**Expected Response**:
```json
{
  "status": "success",
  "count": 3,
  "jobs": [
    {"id": 371692, "datetime_pulled": "2022-07-29T00:50:39.404286Z"},
    {"id": 395736, "datetime_pulled": "2023-01-23T05:18:04.835561Z"},
    {"id": 4354640, "datetime_pulled": "2022-10-05T02:18:10.063525Z"}
  ]
}
```

---

## Additional Example Queries

### Single Condition Query

Simple query for Python jobs:

```bash
curl -X POST "http://localhost:8000/api/v1/jobs/search" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "condition",
    "condition": {
      "field": "technology",
      "value": "python"
    }
  }'
```

### Complex Nested Query

(Google OR Microsoft) AND Python:

```bash
curl -X POST "http://localhost:8000/api/v1/jobs/search" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "operator",
    "operator": "AND",
    "children": [
      {
        "type": "operator",
        "operator": "OR",
        "children": [
          {
            "type": "condition",
            "condition": {
              "field": "organization",
              "value": "google"
            }
          },
          {
            "type": "condition",
            "condition": {
              "field": "organization",
              "value": "microsoft"
            }
          }
        ]
      },
      {
        "type": "condition",
        "condition": {
          "field": "technology",
          "value": "python"
        }
      }
    ]
  }'
```

### Query with Custom Limit

Limit results to 5 jobs:

```bash
curl -X POST "http://localhost:8000/api/v1/jobs/search?limit=5" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "condition",
    "condition": {
      "field": "technology",
      "value": "javascript"
    }
  }'
```

## Health Check

```bash
curl http://localhost:8000/api/v1/health
```

## API Documentation

For interactive API documentation, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

