import React, { useState } from 'react';
import { Send, Loader2, Sparkles } from 'lucide-react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';

interface QueryInputProps {
  onSubmit: (query: string) => void;
  isLoading: boolean;
}

const EXAMPLE_QUERIES = [
  "courses that teach React and frontend jobs requiring React",
  "compare software engineering courses that teach cloud skills with frontend jobs",
  "list courses for BTech graduates and frontend roles that accept BTech",
  "frontend jobs with remote work and software courses offering online delivery",
];

export const QueryInput: React.FC<QueryInputProps> = ({ onSubmit, isLoading }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSubmit(query.trim());
    }
  };

  const handleExampleClick = (exampleQuery: string) => {
    setQuery(exampleQuery);
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-primary" />
          Natural Language Query
        </CardTitle>
        <CardDescription>
          Ask questions about courses and jobs in plain English
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., Find courses that teach React and jobs requiring React..."
              className="min-h-[120px] resize-none"
              disabled={isLoading}
            />
          </div>

          <div className="flex flex-wrap gap-2">
            <span className="text-sm text-muted-foreground self-center">Examples:</span>
            {EXAMPLE_QUERIES.map((example, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleExampleClick(example)}
                disabled={isLoading}
                className="text-xs px-3 py-1.5 rounded-full bg-secondary hover:bg-secondary/80 transition-colors disabled:opacity-50"
              >
                {example.substring(0, 40)}...
              </button>
            ))}
          </div>

          <Button
            type="submit"
            disabled={!query.trim() || isLoading}
            className="w-full"
            size="lg"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing Query...
              </>
            ) : (
              <>
                <Send className="mr-2 h-4 w-4" />
                Execute Query
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};
