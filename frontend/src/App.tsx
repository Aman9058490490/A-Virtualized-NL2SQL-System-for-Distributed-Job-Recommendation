import React, { useState } from 'react';
import { Database, AlertCircle, Activity } from 'lucide-react';
import { QueryInput } from './components/QueryInput';
import { SQLDisplay } from './components/SQLDisplay';
import { ResultsTable } from './components/ResultsTable';
import { FinalAnswer } from './components/FinalAnswer';
import { ThemeToggle } from './components/ThemeToggle';
import { queryAPI, type QueryResponse } from './lib/api';
import './index.css';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [queryResponse, setQueryResponse] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleQuerySubmit = async (query: string) => {
    setIsLoading(true);
    setError(null);
    setQueryResponse(null);

    try {
      const response = await queryAPI.executeQuery(query);
      setQueryResponse(response);
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to execute query';
      setError(errorMessage);
      console.error('Query execution error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      {/* Header */}
      <header className="border-b bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-blue-500 to-indigo-600 p-2 rounded-lg">
                <Database className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  Federated NL2SQL
                </h1>
                <p className="text-xs text-muted-foreground">
                  Natural Language Database Queries
                </p>
              </div>
            </div>
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Query Input */}
          <div className="animate-fade-in">
            <QueryInput onSubmit={handleQuerySubmit} isLoading={isLoading} />
          </div>

          {/* Loading State */}
          {isLoading && (
            <div className="flex flex-col items-center justify-center py-16 space-y-4 animate-fade-in">
              <Activity className="w-12 h-12 text-primary animate-pulse" />
              <div className="text-center">
                <p className="text-lg font-medium">Processing your query...</p>
                <p className="text-sm text-muted-foreground">
                  Analyzing natural language, generating SQL, and fetching results
                </p>
              </div>
            </div>
          )}

          {/* Error State */}
          {error && !isLoading && (
            <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-6 animate-fade-in">
              <div className="flex gap-3">
                <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-destructive mb-1">
                    Query Execution Failed
                  </h3>
                  <p className="text-sm text-destructive/90">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Results */}
          {queryResponse && !isLoading && (
            <div className="space-y-6 animate-fade-in">
              {/* SQL Display */}
              <SQLDisplay
                courseSql={queryResponse.decomposition.course_sql}
                jobSql={queryResponse.decomposition.job_sql}
                naturalQuery={queryResponse.decomposition.natural_query}
              />

              {/* Data Tables */}
              <ResultsTable
                courseResults={queryResponse.results.course}
                jobResults={queryResponse.results.job}
                mergedResults={queryResponse.results.merged}
              />

              {/* Final Answer */}
              <FinalAnswer answer={queryResponse.final_answer} />
            </div>
          )}

          {/* Empty State */}
          {!isLoading && !queryResponse && !error && (
            <div className="flex flex-col items-center justify-center py-16 space-y-4 text-muted-foreground">
              <Database className="w-16 h-16 opacity-20" />
              <div className="text-center max-w-md">
                <p className="text-lg font-medium mb-2">Ready to query your databases</p>
                <p className="text-sm">
                  Enter a natural language query above to search across course and job databases.
                  Our AI will decompose it, generate SQL, merge results, and provide insights.
                </p>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t mt-16 py-6 bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm">
        <div className="container mx-auto px-4">
          <p className="text-center text-sm text-muted-foreground">
            Powered by AI-driven ETL merging • React + Flask + Groq LLM
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
