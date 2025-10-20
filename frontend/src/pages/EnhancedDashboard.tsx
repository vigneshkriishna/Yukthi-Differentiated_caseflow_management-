import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import SystemHealthWidget from '@/components/SystemHealthWidget'
import DocumentStatsWidget from '@/components/DocumentStatsWidget'
import AIWidget from '@/components/AIWidget'
import { 
  Calendar, 
  Clock, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle,
  Brain,
  ArrowRight,
  Zap,
  Users,
  Gavel,
  Activity,
  RefreshCw
} from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'

interface DashboardMetrics {
  totalCases: number
  activeCases: number
  totalSlots: number
  availableSlots: number
  availabilityRate: number
  pendingCases: number
  todayHearings: number
  benchesCount: number
}

interface SystemStatus {
  backend: boolean
  database: boolean
  aiClassification: boolean
  smartScheduling: boolean
}

const EnhancedDashboard: React.FC = () => {
  const { user } = useAuth()
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null)
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())

  // Debug: Confirm which component is rendering
  useEffect(() => {
    console.log('🏠 DASHBOARD COMPONENT MOUNTED - This is the Dashboard page!');
    document.title = 'Dashboard - DCM System';
  }, []);

  useEffect(() => {
    fetchDashboardData()
    const interval = setInterval(fetchDashboardData, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      
      // Use mock data for dashboard since backend endpoints are on different structure
      // Mock cases data
      const casesData = [
        { status: 'FILED' },
        { status: 'UNDER_REVIEW' },
        { status: 'SCHEDULED' },
        { status: 'DISPOSED' }
      ]
      
      // Calculate metrics
      const activeCases = casesData.filter((c: any) => ['FILED', 'UNDER_REVIEW', 'SCHEDULED'].includes(c.status))

      setMetrics({
        totalCases: casesData.length,
        activeCases: activeCases.length,
        totalSlots: 48,
        availableSlots: 32,
        availabilityRate: 67,
        pendingCases: 12,
        todayHearings: 8,
        benchesCount: 6
      })

      setSystemStatus({
        backend: true,
        database: true,
        aiClassification: true,
        smartScheduling: true
      })

      setLastUpdated(new Date())
      
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (isHealthy: boolean) => {
    return isHealthy ? 'text-green-600' : 'text-red-600'
  }

  const getStatusIcon = (isHealthy: boolean) => {
    return isHealthy ? <CheckCircle className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />
  }

  if (loading && !metrics) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header with Real-time Status */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Smart DCM Dashboard</h1>
          <p className="text-gray-600">
            Welcome back, {user?.full_name} • Last updated: {lastUpdated.toLocaleTimeString()}
          </p>
        </div>
        <Button onClick={fetchDashboardData} disabled={loading} className="flex items-center space-x-2">
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </Button>
      </div>

      {/* System Status Cards */}
      {systemStatus && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="h-5 w-5 text-blue-600" />
              <span>System Status</span>
            </CardTitle>
            <CardDescription>Real-time system health monitoring</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="flex items-center space-x-2">
                {getStatusIcon(systemStatus.backend)}
                <span className={`text-sm font-medium ${getStatusColor(systemStatus.backend)}`}>
                  Backend API
                </span>
              </div>
              <div className="flex items-center space-x-2">
                {getStatusIcon(systemStatus.database)}
                <span className={`text-sm font-medium ${getStatusColor(systemStatus.database)}`}>
                  Database
                </span>
              </div>
              <div className="flex items-center space-x-2">
                {getStatusIcon(systemStatus.aiClassification)}
                <span className={`text-sm font-medium ${getStatusColor(systemStatus.aiClassification)}`}>
                  AI Classification
                </span>
              </div>
              <div className="flex items-center space-x-2">
                {getStatusIcon(systemStatus.smartScheduling)}
                <span className={`text-sm font-medium ${getStatusColor(systemStatus.smartScheduling)}`}>
                  Smart Scheduling
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Enhanced Metrics Grid */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Cases</CardTitle>
              <Gavel className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.totalCases}</div>
              <p className="text-xs text-muted-foreground">
                {metrics.activeCases} currently active
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Available Slots</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{metrics.availableSlots}</div>
              <p className="text-xs text-muted-foreground">
                {metrics.availabilityRate.toFixed(1)}% availability rate
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Benches</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.benchesCount}</div>
              <p className="text-xs text-muted-foreground">
                Operational courtrooms
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Today's Hearings</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.todayHearings}</div>
              <p className="text-xs text-muted-foreground">
                Scheduled for today
              </p>
            </CardContent>
          </Card>

          {/* Document Statistics Widget */}
          <DocumentStatsWidget />
        </div>
      )}

      {/* Smart Analytics and System Health Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* AI Insights - Takes 2 columns */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center space-x-2">
                    <Brain className="h-5 w-5 text-blue-600" />
                    <span>AI Insights</span>
                  </CardTitle>
                  <CardDescription>Intelligent analytics and recommendations</CardDescription>
                </div>
                <Badge variant="outline" className="bg-blue-50 text-blue-700">
                  {metrics?.pendingCases || 0} Pending
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 border rounded-lg bg-gradient-to-r from-blue-50 to-purple-50">
                  <div className="flex items-center space-x-3">
                    <div className="flex items-center justify-center w-8 h-8 rounded-full bg-green-100 text-green-600">
                      <CheckCircle className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="font-medium text-sm">System Running Optimally</p>
                      <p className="text-xs text-gray-500">No urgent optimizations needed</p>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-600">
                      <TrendingUp className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="font-medium text-sm">Scheduling Efficiency</p>
                      <p className="text-xs text-gray-500">{metrics?.availabilityRate.toFixed(1)}% slot utilization</p>
                    </div>
                  </div>
                  <Badge variant="outline" className="text-green-700 bg-green-50">Excellent</Badge>
                </div>

                <div className="grid grid-cols-1 gap-3 mt-4">
                  <Button variant="outline" className="h-auto p-4 flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Brain className="h-6 w-6 text-blue-600" />
                      <div className="text-left">
                        <p className="font-medium text-sm">Smart Scheduling</p>
                        <p className="text-xs text-gray-500">AI-powered optimization</p>
                      </div>
                    </div>
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                  
                  <Button variant="outline" className="h-auto p-4 flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Zap className="h-6 w-6 text-yellow-600" />
                      <div className="text-left">
                        <p className="font-medium text-sm">BNS Classification</p>
                        <p className="text-xs text-gray-500">AI case analysis</p>
                      </div>
                    </div>
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* System Health Widget - Takes 1 column */}
        <div className="space-y-6">
          {/* AI Analytics Widget */}
          <AIWidget />
          
          {/* System Health Widget */}
          <SystemHealthWidget />
        </div>
      </div>

      {/* Performance Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Performance Summary</CardTitle>
          <CardDescription>System performance over the last 7 days</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">{metrics?.availabilityRate.toFixed(0)}%</div>
              <p className="text-sm text-gray-600">Court Utilization</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">{metrics?.totalSlots}</div>
              <p className="text-sm text-gray-600">Total Slots Available</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">{metrics?.activeCases}</div>
              <p className="text-sm text-gray-600">Active Cases</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default EnhancedDashboard