import React, { useState } from 'react';
import { Code2, Copy, Check } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface SQLDisplayProps {
  courseSql: string | null;
  jobSql: string | null;
  naturalQuery: string | null;
}

export const SQLDisplay: React.FC<SQLDisplayProps> = ({ courseSql, jobSql, naturalQuery }) => {
  const [copiedCourse, setCopiedCourse] = useState(false);
  const [copiedJob, setCopiedJob] = useState(false);

  const copyToClipboard = async (text: string, type: 'course' | 'job') => {
    await navigator.clipboard.writeText(text);
    if (type === 'course') {
      setCopiedCourse(true);
      setTimeout(() => setCopiedCourse(false), 2000);
    } else {
      setCopiedJob(true);
      setTimeout(() => setCopiedJob(false), 2000);
    }
  };

  if (!courseSql && !jobSql) {
    return null;
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Code2 className="w-5 h-5 text-primary" />
          Generated SQL Queries
        </CardTitle>
        {naturalQuery && (
          <p className="text-sm text-muted-foreground mt-2">
            Natural query: <span className="italic">{naturalQuery}</span>
          </p>
        )}
      </CardHeader>
      <CardContent>
        <Tabs defaultValue={courseSql ? "course" : "job"} className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            {courseSql && <TabsTrigger value="course">Course Database</TabsTrigger>}
            {jobSql && <TabsTrigger value="job">Job Database</TabsTrigger>}
          </TabsList>

          {courseSql && (
            <TabsContent value="course" className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">CourseDB Query</span>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => copyToClipboard(courseSql, 'course')}
                >
                  {copiedCourse ? (
                    <Check className="h-4 w-4 text-green-500" />
                  ) : (
                    <Copy className="h-4 w-4" />
                  )}
                </Button>
              </div>
              <div className="rounded-lg overflow-hidden border">
                <SyntaxHighlighter
                  language="sql"
                  style={vscDarkPlus}
                  customStyle={{
                    margin: 0,
                    fontSize: '0.875rem',
                    maxHeight: '300px',
                  }}
                >
                  {courseSql}
                </SyntaxHighlighter>
              </div>
            </TabsContent>
          )}

          {jobSql && (
            <TabsContent value="job" className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">JobDB Query</span>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => copyToClipboard(jobSql, 'job')}
                >
                  {copiedJob ? (
                    <Check className="h-4 w-4 text-green-500" />
                  ) : (
                    <Copy className="h-4 w-4" />
                  )}
                </Button>
              </div>
              <div className="rounded-lg overflow-hidden border">
                <SyntaxHighlighter
                  language="sql"
                  style={vscDarkPlus}
                  customStyle={{
                    margin: 0,
                    fontSize: '0.875rem',
                    maxHeight: '300px',
                  }}
                >
                  {jobSql}
                </SyntaxHighlighter>
              </div>
            </TabsContent>
          )}
        </Tabs>
      </CardContent>
    </Card>
  );
};
