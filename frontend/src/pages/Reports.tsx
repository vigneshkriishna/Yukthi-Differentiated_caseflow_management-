import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, Download, BarChart3, TrendingUp, FileText } from 'lucide-react';
import toast from 'react-hot-toast';

const Reports: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [caseStats, setCaseStats] = useState<any>(null);

  useEffect(() => {
    loadReportsData();
  }, []);

  const loadReportsData = async () => {
    try {
      setLoading(true);
      
      // Use mock data until backend endpoints are available
      const mockDashboardData = {
        summary: {
          total_cases: 156,
          active_cases: 89,
          completed_cases: 67,
          pending_hearings: 42
        },
        trends: {
          cases_this_month: 23,
          cases_last_month: 19,
          growth_rate: 21.1
        },
        avgCaseResolutionDays: 45
      };
      
      const mockCaseStats = {
        totalCases: 156,
        activeCases: 89,
        completedCases: 67,
        casesByType: {
          'Criminal': 45,
          'Civil': 62,
          'Family': 28,
          'Commercial': 21
        },
        casesByStatus: {
          'Filed': 34,
          'Under Review': 25,
          'Scheduled': 30,
          'In Progress': 12,
          'Disposed': 55
        },
        monthlyStats: [
          { month: 'Jan', filed: 12, disposed: 8 },
          { month: 'Feb', filed: 15, disposed: 10 },
          { month: 'Mar', filed: 18, disposed: 12 },
          { month: 'Apr', filed: 14, disposed: 15 },
          { month: 'May', filed: 19, disposed: 11 },
          { month: 'Jun', filed: 16, disposed: 14 }
        ]
      };
      
      setDashboardData(mockDashboardData);
      setCaseStats(mockCaseStats);
      
    } catch (error) {
      console.error('Error loading reports data:', error);
      toast.error('Failed to load reports data');
    } finally {
      setLoading(false);
    }
  };

  const generateReport = (type: string) => {
    console.log(`Generating ${type} report...`);
    toast.success(`${type} report generation started. You will be notified when it's ready.`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading reports...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Reports & Analytics</h1>
          <p className="text-gray-600">Comprehensive system analytics and reporting</p>
        </div>
        <Button variant="outline">
          <Download className="h-4 w-4 mr-2" />
          Export Data
        </Button>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Cases</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {caseStats?.totalCases?.toLocaleString() || '0'}
            </div>
            <p className="text-xs text-muted-foreground">All time</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Cases</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {caseStats?.activeCases?.toLocaleString() || '0'}
            </div>
            <p className="text-xs text-muted-foreground">Currently active</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed Cases</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {caseStats?.completedCases?.toLocaleString() || '0'}
            </div>
            <p className="text-gray-600">Disposed cases</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Avg Resolution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-purple-600">
              {dashboardData?.avgCaseResolutionDays || '0'}
            </div>
            <p className="text-gray-600">Days to resolve</p>
          </CardContent>
        </Card>
      </div>

      {/* Cases by Type */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Card>
          <CardHeader>
            <CardTitle>Cases by Type</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {caseStats?.casesByType && Object.entries(caseStats.casesByType).map(([type, count]) => (
                <div key={type} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-3 ${
                      type === 'criminal' ? 'bg-red-500' :
                      type === 'civil' ? 'bg-blue-500' :
                      type === 'family' ? 'bg-green-500' :
                      'bg-purple-500'
                    }`}></div>
                    <span className="capitalize">{type}</span>
                  </div>
                  <span className="font-semibold">{count as number}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Cases by Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {caseStats?.casesByStatus && Object.entries(caseStats.casesByStatus).map(([status, count]) => (
                <div key={status} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-3 ${
                      status === 'filed' ? 'bg-yellow-500' :
                      status === 'under_review' ? 'bg-orange-500' :
                      status === 'scheduled' ? 'bg-blue-500' :
                      status === 'hearing' ? 'bg-purple-500' :
                      status === 'judgment_reserved' ? 'bg-indigo-500' :
                      status === 'disposed' ? 'bg-green-500' :
                      'bg-gray-500'
                    }`}></div>
                    <span className="capitalize">{status.replace('_', ' ')}</span>
                  </div>
                  <span className="font-semibold">{count as number}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Monthly Statistics */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Monthly Filing & Disposal Trends</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Month</th>
                  <th className="text-left p-2">Cases Filed</th>
                  <th className="text-left p-2">Cases Disposed</th>
                  <th className="text-left p-2">Net Change</th>
                </tr>
              </thead>
              <tbody>
                {caseStats?.monthlyStats?.map((stat: any) => (
                  <tr key={stat.month} className="border-b">
                    <td className="p-2">{stat.month}</td>
                    <td className="p-2 text-blue-600">{stat.filed}</td>
                    <td className="p-2 text-green-600">{stat.disposed}</td>
                    <td className={`p-2 ${stat.filed - stat.disposed >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                      {stat.filed - stat.disposed > 0 ? '+' : ''}{stat.filed - stat.disposed}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Report Generation */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Case Reports</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button 
              variant="outline" 
              className="w-full justify-start"
              onClick={() => generateReport('Monthly Case Summary')}
            >
              Monthly Case Summary
            </Button>
            <Button 
              variant="outline" 
              className="w-full justify-start"
              onClick={() => generateReport('Case Type Analysis')}
            >
              Case Type Analysis
            </Button>
            <Button 
              variant="outline" 
              className="w-full justify-start"
              onClick={() => generateReport('Pending Cases Report')}
            >
              Pending Cases Report
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Hearing Reports</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button 
              variant="outline" 
              className="w-full justify-start"
              onClick={() => generateReport('Hearing Schedule Report')}
            >
              Hearing Schedule Report
            </Button>
            <Button 
              variant="outline" 
              className="w-full justify-start"
              onClick={() => generateReport('Bench Utilization Report')}
            >
              Bench Utilization Report
            </Button>
            <Button 
              variant="outline" 
              className="w-full justify-start"
              onClick={() => generateReport('Hearing Outcomes Report')}
            >
              Hearing Outcomes Report
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Performance Reports</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button 
              variant="outline" 
              className="w-full justify-start"
              onClick={() => generateReport('Case Resolution Time Report')}
            >
              Case Resolution Time
            </Button>
            <Button 
              variant="outline" 
              className="w-full justify-start"
              onClick={() => generateReport('Judge Performance Report')}
            >
              Judge Performance
            </Button>
            <Button 
              variant="outline" 
              className="w-full justify-start"
              onClick={() => generateReport('Court Efficiency Report')}
            >
              Court Efficiency
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Reports;
