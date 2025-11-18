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

