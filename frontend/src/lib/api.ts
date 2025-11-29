import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export interface QueryDecomposition {
  course_sql: string | null;
  job_sql: string | null;
  natural_query: string | null;
}

export interface DataFrameResult {
  columns: string[];
  data: Record<string, any>[];
  row_count: number;
}

export interface QueryResults {
  course: DataFrameResult;
  job: DataFrameResult;
  merged: DataFrameResult;
}

export interface QueryResponse {
  success: boolean;
  query: string;
  decomposition: QueryDecomposition;
  results: QueryResults;
  final_answer: string;
  error?: string;
  error_type?: string;
}

export interface BatchQueryResult {
  success: boolean;
  query: string;
  course_sql?: string;
  job_sql?: string;
  row_counts?: {
    course: number;
    job: number;
    merged: number;
  };
  final_answer?: string;
  error?: string;
}

export interface BatchResponse {
  success: boolean;
  total_queries: number;
  results: BatchQueryResult[];
  error?: string;
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 2 minutes timeout
});

export const queryAPI = {
  // Health check
  healthCheck: async () => {
    const response = await api.get('/api/health');
    return response.data;
  },

  // Execute single query
  executeQuery: async (query: string, maxRows: number = 100): Promise<QueryResponse> => {
    const response = await api.post<QueryResponse>('/api/query', {
      query,
      max_rows: maxRows,
    });
    return response.data;
  },

  // Execute batch queries
  executeBatch: async (queries: string[], maxRows: number = 50): Promise<BatchResponse> => {
    const response = await api.post<BatchResponse>('/api/query/batch', {
      queries,
      max_rows: maxRows,
    });
    return response.data;
  },

  // Get fallback examples
  getFallbackExamples: async (): Promise<string[]> => {
    const response = await api.get('/api/fallback-examples');
    return response.data.examples;
  },
};

export default api;
