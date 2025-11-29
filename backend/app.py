"""
Flask REST API for Federated NL2SQL
Provides endpoints for query execution and management
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import pandas as pd
from typing import Dict, Any
import traceback
import sys
import os

# Add parent directory to path to import project modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from executor import DatabaseExecutor
from groq_client import GroqClient, GroqClientError
from query_analyzer import QueryAnalyzer
from innovation1 import auto_merge_dataframes
from utils import configure_logging

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configure logging
configure_logging()
logger = logging.getLogger(__name__)

# Initialize components
groq_client = GroqClient()
query_analyzer = QueryAnalyzer(groq_client)
db_executor = DatabaseExecutor()


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Federated NL2SQL API',
        'version': '1.0.0'
    })


@app.route('/api/query', methods=['POST'])
def execute_query():
    """
    Execute a natural language query
    
    Request Body:
    {
        "query": "natural language query string",
        "max_rows": 10 (optional)
    }
    
    Response:
    {
        "success": true,
        "query": "...",
        "decomposition": {...},
        "results": {...},
        "final_answer": "..."
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'Query is required in request body'
            }), 400
        
        nl_query = data['query'].strip()
        max_rows = data.get('max_rows', 100)
        
        if not nl_query:
            return jsonify({
                'success': False,
                'error': 'Query cannot be empty'
            }), 400
        
        logger.info(f"Processing query: {nl_query}")
        
        # Step 1: Decompose query
        decomposition = query_analyzer.generate_decomposition(nl_query)
        
        decomp_dict = {
            'course_sql': decomposition.course_sql,
            'job_sql': decomposition.job_sql,
            'natural_query': decomposition.natural_query
        }
        
        # Step 2: Execute SQL queries
        raw_results = db_executor.execute(
            decomposition.course_sql or "",
            decomposition.job_sql or ""
        )
        
        course_df = raw_results['course']
        job_df = raw_results['job']
        
        # Step 3: Merge using AI ETL
        merged_df = auto_merge_dataframes(course_df, job_df)
        
        # Step 4: Generate final answer
        final_answer = db_executor.generate_final_answer(
            merged_df,
            decomposition.natural_query,
            nl_query
        )
        
        # Convert dataframes to JSON-serializable format
        def df_to_dict(df: pd.DataFrame, limit: int) -> Dict[str, Any]:
            if df.empty:
                return {'columns': [], 'data': [], 'row_count': 0}
            
            limited_df = df.head(limit)
            return {
                'columns': limited_df.columns.tolist(),
                'data': limited_df.to_dict('records'),
                'row_count': len(df)
            }
        
        response = {
            'success': True,
            'query': nl_query,
            'decomposition': decomp_dict,
            'results': {
                'course': df_to_dict(course_df, max_rows),
                'job': df_to_dict(job_df, max_rows),
                'merged': df_to_dict(merged_df, max_rows)
            },
            'final_answer': final_answer
        }
        
        return jsonify(response)
    
    except GroqClientError as e:
        logger.error(f"LLM Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'LLM API error: {str(e)}',
            'error_type': 'llm_error'
        }), 500
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'server_error'
        }), 500


@app.route('/api/query/batch', methods=['POST'])
def execute_batch():
    """
    Execute multiple queries in batch
    
    Request Body:
    {
        "queries": ["query1", "query2", ...],
        "max_rows": 10 (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'queries' not in data:
            return jsonify({
                'success': False,
                'error': 'Queries array is required'
            }), 400
        
        queries = data['queries']
        max_rows = data.get('max_rows', 50)
        
        if not isinstance(queries, list):
            return jsonify({
                'success': False,
                'error': 'Queries must be an array'
            }), 400
        
        results = []
        
        for query in queries:
            try:
                # Reuse single query logic
                decomposition = query_analyzer.generate_decomposition(query)
                raw_results = db_executor.execute(
                    decomposition.course_sql or "",
                    decomposition.job_sql or ""
                )
                
                merged_df = auto_merge_dataframes(
                    raw_results['course'],
                    raw_results['job']
                )
                
                final_answer = db_executor.generate_final_answer(
                    merged_df,
                    decomposition.natural_query,
                    query
                )
                
                results.append({
                    'success': True,
                    'query': query,
                    'course_sql': decomposition.course_sql,
                    'job_sql': decomposition.job_sql,
                    'row_counts': {
                        'course': len(raw_results['course']),
                        'job': len(raw_results['job']),
                        'merged': len(merged_df)
                    },
                    'final_answer': final_answer
                })
                
            except Exception as e:
                results.append({
                    'success': False,
                    'query': query,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'total_queries': len(queries),
            'results': results
        })
    
    except Exception as e:
        logger.error(f"Batch error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/fallback-examples', methods=['GET'])
def get_fallback_examples():
    """Get preset fallback example queries"""
    examples = [
        "courses that teach React and frontend jobs requiring React",
        "compare software engineering courses that teach cloud skills with frontend jobs requiring cloud integrations",
        "which courses map to frontend jobs requiring TypeScript and 3 to 5 years experience",
        "list courses for BTech graduates and frontend roles that accept BTech",
        "compare salaries between backend software roles and frontend roles for candidates with 5 years experience",
        "find frontend jobs that prefer female candidates and software courses that support leadership skills",
        "which courses help frontend developers become full stack engineers and what job openings match that transition",
        "top skills taught in software courses that match frontend job postings requiring Vue.js or React",
        "frontend jobs with remote work and software courses offering online delivery",
        "courses that teach UX design and frontend jobs seeking UX skills with 2-4 years experience"
    ]
    
    return jsonify({
        'success': True,
        'examples': examples
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
