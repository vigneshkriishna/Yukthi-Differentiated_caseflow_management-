import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  RefreshCw,
  FolderOpen
} from 'lucide-react';

interface DocumentStats {
  total: number;
  recentUploads: number;
  totalSize: number;
  byType: Record<string, number>;
  topTypes: Array<{ type: string; count: number; percentage: number }>;
}

const API_BASE = 'http://localhost:8001';

const DocumentStatsWidget: React.FC = () => {
  const [stats, setStats] = useState<DocumentStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>('');

  const getAuthToken = () => {
    return localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
  };

  const fetchDocumentStats = async () => {
    const token = getAuthToken();
    if (!token) return;

    try {
      setIsLoading(true);
      const response = await fetch(`${API_BASE}/api/documents`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const documents = await response.json();
        calculateStats(documents);
        setError('');
      } else if (response.status === 401) {
        setError('Authentication required');
      } else {
        setError('Failed to load document statistics');
      }
    } catch (err) {
      setError('Network error');
      console.error('Error loading document stats:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const calculateStats = (documents: any[]) => {
    const now = new Date();
    const twentyFourHoursAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);

    const byType: Record<string, number> = {};
    let totalSize = 0;
    let recentUploads = 0;

    documents.forEach(doc => {
      byType[doc.document_type] = (byType[doc.document_type] || 0) + 1;
      totalSize += doc.size;
      
      if (new Date(doc.upload_date) > twentyFourHoursAgo) {
        recentUploads++;
      }
    });

    // Get top 3 document types
    const topTypes = Object.entries(byType)
      .map(([type, count]) => ({
        type: type.charAt(0).toUpperCase() + type.slice(1),
        count,
        percentage: Math.round((count / documents.length) * 100)
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 3);

    setStats({
      total: documents.length,
      recentUploads,
      totalSize,
      byType,
      topTypes
    });
  };

  useEffect(() => {
    fetchDocumentStats();
  }, []);

  if (isLoading) {
    return (
      <Card className="h-full">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Document Statistics</CardTitle>
          <FolderOpen className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="h-full">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Document Statistics</CardTitle>
          <FolderOpen className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-center py-6">
            <p className="text-sm text-muted-foreground">{error}</p>
            <Button
              variant="outline"
              size="sm"
              onClick={fetchDocumentStats}
              className="mt-2"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!stats) return null;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Documents</CardTitle>
        <FolderOpen className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{stats.total}</div>
        <p className="text-xs text-muted-foreground">
          {stats.recentUploads > 0 ? `+${stats.recentUploads} uploaded today` : 'Total documents in system'}
        </p>
      </CardContent>
    </Card>
  );
};

export default DocumentStatsWidget;