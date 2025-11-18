#!/usr/bin/env python3
"""
Comprehensive test suite for the Sumble Advanced Query API.
Tests various query patterns and measures performance metrics.
"""

import asyncio
import httpx
import time
import statistics
from typing import Dict, List, Any
from dataclasses import dataclass
import json


@dataclass
class TestResult:
    name: str
    query: Dict[str, Any]
    limit: int
    success: bool
    status_code: int
    response_time_ms: float
    job_count: int
    error: str = None


class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[TestResult] = []
    
    async def test_query(self, name: str, query: Dict[str, Any], limit: int = 10) -> TestResult:
        """Test a single query and measure performance."""
        url = f"{self.base_url}/api/v1/jobs/search"
        
        start_time = time.perf_counter()
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url,
                    json=query,
                    params={"limit": limit}
                )
                
                end_time = time.perf_counter()
                response_time_ms = (end_time - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    result = TestResult(
                        name=name,
                        query=query,
                        limit=limit,
                        success=True,
                        status_code=response.status_code,
                        response_time_ms=response_time_ms,
                        job_count=data.get("count", 0)
                    )
                else:
                    result = TestResult(
                        name=name,
                        query=query,
                        limit=limit,
                        success=False,
                        status_code=response.status_code,
                        response_time_ms=response_time_ms,
                        job_count=0,
                        error=response.text
                    )
        except Exception as e:
            end_time = time.perf_counter()
            response_time_ms = (end_time - start_time) * 1000
            result = TestResult(
                name=name,
                query=query,
                limit=limit,
                success=False,
                status_code=0,
                response_time_ms=response_time_ms,
                job_count=0,
                error=str(e)
            )
        
        self.results.append(result)
        return result
    
    def print_result(self, result: TestResult):
        """Print a single test result."""
        status = "✅" if result.success else "❌"
        print(f"\n{status} {result.name}")
        print(f"   Limit: {result.limit}")
        print(f"   Response Time: {result.response_time_ms:.2f}ms")
        print(f"   Status Code: {result.status_code}")
        print(f"   Jobs Found: {result.job_count}")
        if result.error:
            print(f"   Error: {result.error[:100]}")
    
    def print_summary(self):
        """Print summary statistics."""
        if not self.results:
            print("\nNo results to summarize.")
            return
        
        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]
        
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"\nTotal Tests: {len(self.results)}")
        print(f"✅ Passed: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")
        
        if successful:
            response_times = [r.response_time_ms for r in successful]
            job_counts = [r.job_count for r in successful]
            
            print("\n" + "-"*80)
            print("PERFORMANCE METRICS (Successful Queries)")
            print("-"*80)
            print(f"Response Time:")
            print(f"  Min:    {min(response_times):.2f}ms")
            print(f"  Max:    {max(response_times):.2f}ms")
            print(f"  Mean:   {statistics.mean(response_times):.2f}ms")
            print(f"  Median: {statistics.median(response_times):.2f}ms")
            if len(response_times) > 1:
                print(f"  StdDev: {statistics.stdev(response_times):.2f}ms")
            
            print(f"\nJob Counts:")
            print(f"  Min:    {min(job_counts)}")
            print(f"  Max:    {max(job_counts)}")
            print(f"  Mean:   {statistics.mean(job_counts):.2f}")
            print(f"  Median: {statistics.median(job_counts):.2f}")
            print(f"  Total:  {sum(job_counts)} jobs across all queries")
        
        if failed:
            print("\n" + "-"*80)
            print("FAILED TESTS")
            print("-"*80)
            for result in failed:
                print(f"\n❌ {result.name}")
                print(f"   Error: {result.error}")


# Test Query Definitions
TEST_QUERIES = [
    # === BASIC SINGLE CONDITION QUERIES ===
    {
        "name": "1. Single Condition - Organization: Apple",
        "limit": 10,
        "query": {
            "type": "condition",
            "condition": {"field": "organization", "value": "apple"}
        }
    },
    {
        "name": "2. Single Condition - Technology: Python",
        "limit": 10,
        "query": {
            "type": "condition",
            "condition": {"field": "technology", "value": "python"}
        }
    },
    {
        "name": "3. Single Condition - Job Function: Engineer",
        "limit": 10,
        "query": {
            "type": "condition",
            "condition": {"field": "job_function", "value": "engineer"}
        }
    },
    
    # === SIMPLE AND QUERIES ===
    {
        "name": "4. AND - Apple + .NET (Required Query 1)",
        "limit": 10,
        "query": {
            "type": "operator",
            "operator": "AND",
            "children": [
                {"type": "condition", "condition": {"field": "organization", "value": "apple"}},
                {"type": "condition", "condition": {"field": "technology", "value": ".net"}}
            ]
        }
    },
    {
        "name": "5. AND - Google + Java",
        "limit": 15,
        "query": {
            "type": "operator",
            "operator": "AND",
            "children": [
                {"type": "condition", "condition": {"field": "organization", "value": "google"}},
                {"type": "condition", "condition": {"field": "technology", "value": "java"}}
            ]
        }
    },
    {
        "name": "6. AND - Microsoft + Data Scientist",
        "limit": 20,
        "query": {
            "type": "operator",
            "operator": "AND",
            "children": [
                {"type": "condition", "condition": {"field": "organization", "value": "microsoft"}},
                {"type": "condition", "condition": {"field": "job_function", "value": "data scientist"}}
            ]
        }
    },
    
    # === SIMPLE OR QUERIES ===
    {
        "name": "7. OR - Python OR JavaScript",
        "limit": 10,
        "query": {
            "type": "operator",
            "operator": "OR",
            "children": [
                {"type": "condition", "condition": {"field": "technology", "value": "python"}},
                {"type": "condition", "condition": {"field": "technology", "value": "javascript"}}
            ]
        }
    },
    {
        "name": "8. OR - Engineer OR Developer",
        "limit": 25,
        "query": {
            "type": "operator",
            "operator": "OR",
            "children": [
                {"type": "condition", "condition": {"field": "job_function", "value": "engineer"}},
                {"type": "condition", "condition": {"field": "job_function", "value": "developer"}}
            ]
        }
    },
    
    # === SIMPLE NOT QUERIES ===
    {
        "name": "9. NOT - NOT Apple",
        "limit": 10,
        "query": {
            "type": "operator",
            "operator": "NOT",
            "children": [
                {"type": "condition", "condition": {"field": "organization", "value": "apple"}}
            ]
        }
    },
    {
        "name": "10. NOT - NOT Java",
        "limit": 10,
        "query": {
            "type": "operator",
            "operator": "NOT",
            "children": [
                {"type": "condition", "condition": {"field": "technology", "value": "java"}}
            ]
        }
    },
    
    # === COMPLEX NESTED QUERIES ===
    {
        "name": "11. NOT AND OR - NOT Apple AND (Statistician OR PSQL) (Required Query 2)",
        "limit": 10,
        "query": {
            "type": "operator",
            "operator": "AND",
            "children": [
                {
                    "type": "operator",
                    "operator": "NOT",
                    "children": [
                        {"type": "condition", "condition": {"field": "organization", "value": "apple"}}
                    ]
                },
                {
                    "type": "operator",
                    "operator": "OR",
                    "children": [
                        {"type": "condition", "condition": {"field": "job_function", "value": "statistician"}},
                        {"type": "condition", "condition": {"field": "technology", "value": "psql"}}
                    ]
                }
            ]
        }
    },
    {
        "name": "12. (Google OR Microsoft) AND Python",
        "limit": 15,
        "query": {
            "type": "operator",
            "operator": "AND",
            "children": [
                {
                    "type": "operator",
                    "operator": "OR",
                    "children": [
                        {"type": "condition", "condition": {"field": "organization", "value": "google"}},
                        {"type": "condition", "condition": {"field": "organization", "value": "microsoft"}}
                    ]
                },
                {"type": "condition", "condition": {"field": "technology", "value": "python"}}
            ]
        }
    },
    {
        "name": "13. Amazon AND (AWS OR Cloud) AND Engineer",
        "limit": 20,
        "query": {
            "type": "operator",
            "operator": "AND",
            "children": [
                {"type": "condition", "condition": {"field": "organization", "value": "amazon"}},
                {
                    "type": "operator",
                    "operator": "OR",
                    "children": [
                        {"type": "condition", "condition": {"field": "technology", "value": "aws"}},
                        {"type": "condition", "condition": {"field": "technology", "value": "cloud"}}
                    ]
                },
                {"type": "condition", "condition": {"field": "job_function", "value": "engineer"}}
            ]
        }
    },
    {
        "name": "14. (Python OR Java) AND (Engineer OR Developer)",
        "limit": 10,
        "query": {
            "type": "operator",
            "operator": "AND",
            "children": [
                {
                    "type": "operator",
                    "operator": "OR",
                    "children": [
                        {"type": "condition", "condition": {"field": "technology", "value": "python"}},
                        {"type": "condition", "condition": {"field": "technology", "value": "java"}}
                    ]
                },
                {
                    "type": "operator",
                    "operator": "OR",
                    "children": [
                        {"type": "condition", "condition": {"field": "job_function", "value": "engineer"}},
                        {"type": "condition", "condition": {"field": "job_function", "value": "developer"}}
                    ]
                }
            ]
        }
    },
    {
        "name": "15. NOT (Google OR Apple) AND Data",
        "limit": 30,
        "query": {
            "type": "operator",
            "operator": "AND",
            "children": [
                {
                    "type": "operator",
                    "operator": "NOT",
                    "children": [
                        {
                            "type": "operator",
                            "operator": "OR",
                            "children": [
                                {"type": "condition", "condition": {"field": "organization", "value": "google"}},
                                {"type": "condition", "condition": {"field": "organization", "value": "apple"}}
                            ]
                        }
                    ]
                },
                {"type": "condition", "condition": {"field": "job_function", "value": "data"}}
            ]
        }
    },
    
    # === DEEPLY NESTED QUERIES ===
    {
        "name": "16. Three-Level Nesting - (A OR B) AND (C OR (D AND E))",
        "limit": 10,
        "query": {
            "type": "operator",
            "operator": "AND",
            "children": [
                {
                    "type": "operator",
                    "operator": "OR",
                    "children": [
                        {"type": "condition", "condition": {"field": "organization", "value": "facebook"}},
                        {"type": "condition", "condition": {"field": "organization", "value": "meta"}}
                    ]
                },
                {
                    "type": "operator",
                    "operator": "OR",
                    "children": [
                        {"type": "condition", "condition": {"field": "technology", "value": "react"}},
                        {
                            "type": "operator",
                            "operator": "AND",
                            "children": [
                                {"type": "condition", "condition": {"field": "technology", "value": "javascript"}},
                                {"type": "condition", "condition": {"field": "job_function", "value": "engineer"}}
                            ]
                        }
                    ]
                }
            ]
        }
    },
    
    # === DIFFERENT LIMIT SIZES ===
    {
        "name": "17. Large Limit - Python jobs (limit=50)",
        "limit": 50,
        "query": {
            "type": "condition",
            "condition": {"field": "technology", "value": "python"}
        }
    },
    {
        "name": "18. Very Large Limit - Engineer jobs (limit=100)",
        "limit": 100,
        "query": {
            "type": "condition",
            "condition": {"field": "job_function", "value": "engineer"}
        }
    },
    {
        "name": "19. Small Limit - SQL jobs (limit=5)",
        "limit": 5,
        "query": {
            "type": "condition",
            "condition": {"field": "technology", "value": "sql"}
        }
    },
    
    # === EDGE CASES ===
    {
        "name": "20. Multiple ANDs - Four conditions",
        "limit": 10,
        "query": {
            "type": "operator",
            "operator": "AND",
            "children": [
                {"type": "condition", "condition": {"field": "organization", "value": "ibm"}},
                {"type": "condition", "condition": {"field": "technology", "value": "java"}},
                {"type": "condition", "condition": {"field": "technology", "value": "cloud"}},
                {"type": "condition", "condition": {"field": "job_function", "value": "engineer"}}
            ]
        }
    },
    {
        "name": "21. Multiple ORs - Five conditions",
        "limit": 15,
        "query": {
            "type": "operator",
            "operator": "OR",
            "children": [
                {"type": "condition", "condition": {"field": "technology", "value": "python"}},
                {"type": "condition", "condition": {"field": "technology", "value": "java"}},
                {"type": "condition", "condition": {"field": "technology", "value": "javascript"}},
                {"type": "condition", "condition": {"field": "technology", "value": "go"}},
                {"type": "condition", "condition": {"field": "technology", "value": "rust"}}
            ]
        }
    },
    {
        "name": "22. Partial Match - 'soft' (matches Microsoft, Software, etc.)",
        "limit": 10,
        "query": {
            "type": "condition",
            "condition": {"field": "organization", "value": "soft"}
        }
    },
    {
        "name": "23. Case Insensitive - 'PYTHON' (uppercase)",
        "limit": 10,
        "query": {
            "type": "condition",
            "condition": {"field": "technology", "value": "PYTHON"}
        }
    },
]


async def main():
    print("="*80)
    print("SUMBLE ADVANCED QUERY API - COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    tester = APITester()
    
    # Run all tests
    for test_def in TEST_QUERIES:
        result = await tester.test_query(
            name=test_def["name"],
            query=test_def["query"],
            limit=test_def["limit"]
        )
        tester.print_result(result)
        
        # Small delay between requests
        await asyncio.sleep(0.1)
    
    # Print summary
    tester.print_summary()
    
    # Export results to JSON
    results_json = []
    for r in tester.results:
        results_json.append({
            "name": r.name,
            "limit": r.limit,
            "success": r.success,
            "status_code": r.status_code,
            "response_time_ms": r.response_time_ms,
            "job_count": r.job_count,
            "error": r.error
        })
    
    # Export to reports directory
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    reports_dir = os.path.join(script_dir, "..", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    results_path = os.path.join(reports_dir, "test_results.json")
    
    with open(results_path, "w") as f:
        json.dump(results_json, f, indent=2)
    
    print(f"\n📊 Detailed results exported to reports/test_results.json")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())

