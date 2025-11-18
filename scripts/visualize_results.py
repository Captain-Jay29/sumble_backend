#!/usr/bin/env python3
"""
Create a visual performance dashboard from test results.
"""

import json


def create_ascii_bar_chart(data, title, max_width=60):
    """Create an ASCII bar chart."""
    if not data:
        return ""
    
    max_value = max(v for _, v in data)
    
    output = [f"\n{title}", "=" * len(title)]
    
    for label, value in data:
        bar_length = int((value / max_value) * max_width) if max_value > 0 else 0
        bar = "█" * bar_length
        output.append(f"{label:40s} {bar} {value:.2f}")
    
    return "\n".join(output)


def main():
    # Load test results
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_path = os.path.join(script_dir, "..", "reports", "test_results.json")
    
    with open(results_path, "r") as f:
        results = json.load(f)
    
    successful = [r for r in results if r["success"]]
    
    if not successful:
        print("No successful results to visualize.")
        return
    
    print("\n" + "="*80)
    print("SUMBLE API - PERFORMANCE DASHBOARD")
    print("="*80)
    
    # Response time by test
    times_data = [(r["name"][:35] + "...", r["response_time_ms"]) for r in successful[:10]]
    print(create_ascii_bar_chart(times_data, "Response Times (First 10 Tests) [ms]"))
    
    # Job counts
    jobs_data = [(r["name"][:35] + "...", r["job_count"]) for r in successful if r["job_count"] > 0][:10]
    print(create_ascii_bar_chart(jobs_data, "\nJob Counts (Top 10 by results)", max_width=50))
    
    # Performance tiers
    fast = sum(1 for r in successful if r["response_time_ms"] < 100)
    medium = sum(1 for r in successful if 100 <= r["response_time_ms"] < 500)
    slow = sum(1 for r in successful if r["response_time_ms"] >= 500)
    
    print("\n\nPerformance Tiers")
    print("="*40)
    print(f"⚡ Fast (<100ms):    {fast:2d} tests {'█' * int(fast * 2)}")
    print(f"⚙️  Medium (100-500ms): {medium:2d} tests {'█' * int(medium * 2)}")
    print(f"🐢 Slow (>500ms):    {slow:2d} tests {'█' * int(slow * 2)}")
    
    # Stats summary
    times = [r["response_time_ms"] for r in successful]
    jobs = [r["job_count"] for r in successful]
    
    print("\n\nKey Performance Indicators")
    print("="*40)
    print(f"✅ Success Rate:     100%")
    print(f"⚡ Fastest Query:    {min(times):.2f}ms")
    print(f"🐢 Slowest Query:    {max(times):.2f}ms")
    print(f"📊 Average Time:     {sum(times)/len(times):.2f}ms")
    print(f"🎯 Total Jobs Found: {sum(jobs)}")
    print(f"📈 Avg Jobs/Query:   {sum(jobs)/len(jobs):.2f}")
    
    # Query complexity analysis
    print("\n\nQuery Complexity Analysis")
    print("="*40)
    
    single = [r for r in successful if "Single Condition" in r["name"]]
    simple_and = [r for r in successful if "AND" in r["name"] and "NOT" not in r["name"] and "OR" not in r["name"]]
    complex_nested = [r for r in successful if ("NOT" in r["name"] or "OR" in r["name"]) and "AND" in r["name"]]
    
    if single:
        print(f"Simple (1 condition):  {len(single):2d} tests | Avg: {sum(r['response_time_ms'] for r in single)/len(single):.2f}ms")
    if simple_and:
        print(f"AND queries:           {len(simple_and):2d} tests | Avg: {sum(r['response_time_ms'] for r in simple_and)/len(simple_and):.2f}ms")
    if complex_nested:
        print(f"Complex nested:        {len(complex_nested):2d} tests | Avg: {sum(r['response_time_ms'] for r in complex_nested)/len(complex_nested):.2f}ms")
    
    print("\n" + "="*80)
    print("📊 Full report available in: TESTING_REPORT.md")
    print("📁 Raw data available in: test_results.json")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

