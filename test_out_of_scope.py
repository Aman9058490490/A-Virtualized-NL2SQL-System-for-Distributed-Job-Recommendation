"""
Test script for out-of-scope query handling
Demonstrates how the system now handles queries that fall outside the database scope
"""

from query_analyzer import QueryAnalyzer
from executor import DatabaseExecutor
from groq_client import GroqClient
from innovation1 import auto_merge_dataframes

def test_out_of_scope_query(query: str):
    """Test a single query and print the results"""
    print(f"\n{'='*80}")
    print(f"Testing Query: {query}")
    print(f"{'='*80}")
    
    # Initialize components
    groq_client = GroqClient()
    query_analyzer = QueryAnalyzer(groq_client)
    db_executor = DatabaseExecutor()
    
    try:
        # Step 1: Decompose query
        print("\n[1/4] Decomposing query...")
        decomposition = query_analyzer.generate_decomposition(query)
        
        print(f"  - course_sql: {decomposition.course_sql[:100] if decomposition.course_sql else 'None'}...")
        print(f"  - job_sql: {decomposition.job_sql[:100] if decomposition.job_sql else 'None'}...")
        print(f"  - natural_query: {decomposition.natural_query[:100]}...")
        
        # Step 2: Execute SQL
        print("\n[2/4] Executing SQL queries...")
        raw_results = db_executor.execute(
            decomposition.course_sql or "",
            decomposition.job_sql or ""
        )
        
        print(f"  - Course results: {len(raw_results['course'])} rows")
        print(f"  - Job results: {len(raw_results['job'])} rows")
        
        # Step 3: Merge results
        print("\n[3/4] Merging results...")
        merged_df = auto_merge_dataframes(raw_results['course'], raw_results['job'])
        print(f"  - Merged results: {len(merged_df)} rows")
        
        # Step 4: Generate final answer
        print("\n[4/4] Generating final answer...")
        final_answer = db_executor.generate_final_answer(
            merged_df,
            decomposition.natural_query,
            query
        )
        
        print(f"\n{'─'*80}")
        print("FINAL ANSWER:")
        print(f"{'─'*80}")
        print(final_answer)
        print(f"{'─'*80}\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run tests for various out-of-scope queries"""
    
    print("\n" + "="*80)
    print("OUT-OF-SCOPE QUERY HANDLING TEST SUITE")
    print("="*80)
    
    # Test cases
    test_queries = [
        # Completely out of scope
        "Find me medical jobs for doctors",
        "Show teaching positions for professors",
        "List sales and marketing roles",
        
        # Partially related
        "Jobs for data scientists with machine learning experience",
        "Find positions in the automotive industry",
        
        # Should work normally (in scope)
        "Frontend developer jobs with React experience",
        "Software engineering positions for backend developers",
    ]
    
    results = []
    
    for query in test_queries:
        success = test_out_of_scope_query(query)
        results.append((query, success))
        
        # Add a pause between queries to avoid rate limiting
        import time
        time.sleep(2)
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for query, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {query[:60]}...")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed ({100*passed//total}%)")
    print("="*80 + "\n")


if __name__ == "__main__":
    # You can test a single query like this:
    # test_out_of_scope_query("Find me medical jobs")
    
    # Or run the full test suite:
    main()
