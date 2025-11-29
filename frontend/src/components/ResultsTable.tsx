import React from 'react';
import { Table, Database, FileJson, Download } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Button } from './ui/button';
import type { DataFrameResult } from '@/lib/api';

interface ResultsTableProps {
  courseResults: DataFrameResult;
  jobResults: DataFrameResult;
  mergedResults: DataFrameResult;
}

const DataTable: React.FC<{ data: DataFrameResult; title: string }> = ({ data, title }) => {
  if (!data || data.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
        <Database className="w-12 h-12 mb-4 opacity-50" />
        <p>No results found</p>
      </div>
    );
  }

  const downloadCSV = () => {
    const headers = data.columns.join(',');
    const rows = data.data.map(row =>
      data.columns.map(col => {
        const value = row[col];
        const stringValue = value === null || value === undefined ? '' : String(value);
        return stringValue.includes(',') ? `"${stringValue}"` : stringValue;
      }).join(',')
    );
    const csv = [headers, ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title.toLowerCase().replace(/\s/g, '_')}_results.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadJSON = () => {
    const json = JSON.stringify(data.data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title.toLowerCase().replace(/\s/g, '_')}_results.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <p className="text-sm text-muted-foreground">
            Showing {data.data.length} of {data.row_count} rows
          </p>
        </div>
        <div className="flex gap-2">
          <Button size="sm" variant="outline" onClick={downloadCSV}>
            <Download className="w-4 h-4 mr-2" />
            CSV
          </Button>
          <Button size="sm" variant="outline" onClick={downloadJSON}>
            <FileJson className="w-4 h-4 mr-2" />
            JSON
          </Button>
        </div>
      </div>

      <div className="border rounded-lg overflow-auto max-h-[500px]">
        <table className="w-full text-sm">
          <thead className="bg-muted sticky top-0">
            <tr>
              {data.columns.map((col) => (
                <th key={col} className="px-4 py-3 text-left font-medium">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.data.map((row, idx) => (
              <tr key={idx} className="border-t hover:bg-muted/50 transition-colors">
                {data.columns.map((col) => (
                  <td key={col} className="px-4 py-3">
                    {row[col] === null || row[col] === undefined ? (
                      <span className="text-muted-foreground italic">null</span>
                    ) : (
                      String(row[col])
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export const ResultsTable: React.FC<ResultsTableProps> = ({
  courseResults,
  jobResults,
  mergedResults,
}) => {
  const hasResults = courseResults.data.length > 0 || jobResults.data.length > 0 || mergedResults.data.length > 0;

  if (!hasResults) {
    return null;
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Table className="w-5 h-5 text-primary" />
          Query Results
        </CardTitle>
        <CardDescription>Data fetched from databases and merged using AI-ETL</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="merged" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="merged">
              Merged ({mergedResults.row_count})
            </TabsTrigger>
            <TabsTrigger value="course">
              Course DB ({courseResults.row_count})
            </TabsTrigger>
            <TabsTrigger value="job">
              Job DB ({jobResults.row_count})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="merged">
            <DataTable data={mergedResults} title="Merged Results" />
          </TabsContent>

          <TabsContent value="course">
            <DataTable data={courseResults} title="Course Database" />
          </TabsContent>

          <TabsContent value="job">
            <DataTable data={jobResults} title="Job Database" />
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};
