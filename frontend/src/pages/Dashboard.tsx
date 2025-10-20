import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useAuth, usePermissions } from '@/contexts/AuthContext'
import { casesAPI } from '@/services/api'
import type { Case } from '@/types'
import toast from 'react-hot-toast'
import { 
  FileText, 
  Calendar, 
  TrendingUp, 
  Plus,
  ArrowRight,
  AlertTriangle,
  CheckCircle,
  Loader2
} from 'lucide-react'

interface DashboardStats {
  totalCases: number
  activeCases: number
  pendingHearings: number
  todayHearings: number
  overdueActions: number
  completedThisMonth: number
  casesByType: Record<string, number>
  casesByStatus: Record<string, number>
  casesByPriority: Record<string, number>
}

const Dashboard: React.FC = () => {
  const { user } = useAuth()
  const permissions = usePermissions()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [recentCases, setRecentCases] = useState<Case[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      
      // Load all cases to calculate stats
      const casesResponse = await casesAPI.getAll()
      const cases = casesResponse.data
      
      // Calculate dashboard statistics
      const totalCases = cases.length
      const activeCases = cases.filter(c => !['disposed', 'closed'].includes(c.status.toLowerCase())).length
      const scheduledHearings = cases.filter(c => c.status.toLowerCase() === 'scheduled').length
      const inHearing = cases.filter(c => c.status.toLowerCase() === 'hearing').length
      const underReview = cases.filter(c => c.status.toLowerCase() === 'under_review').length
      
      // Calculate case distribution
      const casesByType: Record<string, number> = {}
      const casesByStatus: Record<string, number> = {}
      const casesByPriority: Record<string, number> = {}
      
      cases.forEach(case_ => {
        casesByType[case_.case_type] = (casesByType[case_.case_type] || 0) + 1
        casesByStatus[case_.status] = (casesByStatus[case_.status] || 0) + 1
        casesByPriority[case_.priority] = (casesByPriority[case_.priority] || 0) + 1
      })
      
      // Get recent cases (last 5 modified)
      const recentCasesData = cases
        .sort((a, b) => new Date(b.created_at || b.filing_date).getTime() - new Date(a.created_at || a.filing_date).getTime())
        .slice(0, 5)
      
      setStats({
        totalCases,
        activeCases,
        pendingHearings: scheduledHearings,
        todayHearings: inHearing,
        overdueActions: underReview,
        completedThisMonth: cases.filter(c => c.status.toLowerCase() === 'disposed').length,
        casesByType,
        casesByStatus,
        casesByPriority
      })
      
      setRecentCases(recentCasesData)
    } catch (error: any) {
      toast.error('Failed to load dashboard data')
      console.error('Dashboard load error:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'hearing': 'bg-blue-100 text-blue-800',
      'under_review': 'bg-yellow-100 text-yellow-800',
      'scheduled': 'bg-purple-100 text-purple-800',
      'disposed': 'bg-green-100 text-green-800',
      'filed': 'bg-gray-100 text-gray-800'
    }
    return colors[status.toLowerCase()] || 'bg-gray-100 text-gray-800'
  }

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      'low': 'bg-gray-100 text-gray-800',
      'medium': 'bg-yellow-100 text-yellow-800',
      'high': 'bg-orange-100 text-orange-800',
      'urgent': 'bg-red-100 text-red-800'
    }
    return colors[priority.toLowerCase()] || 'bg-gray-100 text-gray-800'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading dashboard...</span>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Welcome back, {user?.full_name}</p>
        </div>
        {permissions.canCreate('cases') && (
          <Button>
            <Link to="/cases/new" className="flex items-center">
              <Plus className="h-4 w-4 mr-2" />
              New Case
            </Link>
          </Button>
        )}
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Cases</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.totalCases?.toLocaleString() || '0'}</div>
            <p className="text-xs text-muted-foreground">
              {stats?.activeCases || 0} active cases
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Today's Hearings</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.todayHearings || 0}</div>
            <p className="text-xs text-muted-foreground">
              {stats?.pendingHearings || 0} total pending
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Overdue Actions</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats?.overdueActions || 0}</div>
            <p className="text-xs text-muted-foreground">
              Require immediate attention
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed This Month</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats?.completedThisMonth || 0}</div>
            <p className="text-xs text-muted-foreground">
              <TrendingUp className="h-3 w-3 inline mr-1" />
              +12% from last month
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Cases */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Recent Cases</CardTitle>
              <Button variant="outline" size="sm">
                <Link to="/cases" className="flex items-center">
                  View All
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Link>
              </Button>
            </div>
            <CardDescription>
              Latest case updates and assignments
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentCases.map((case_) => (
                <div key={case_.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="font-medium text-sm">{case_.case_number}</span>
                      <Badge className={getPriorityColor(case_.priority)}>
                        {case_.priority}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600 mb-1">{case_.title}</p>
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      <span className="flex items-center">
                        <FileText className="h-3 w-3 mr-1" />
                        {case_.case_type}
                      </span>
                      <span className="flex items-center">
                        <Calendar className="h-3 w-3 mr-1" />
                        {new Date(case_.filing_date).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <Badge className={getStatusColor(case_.status)}>
                    {case_.status.replace('_', ' ')}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Today's Hearings */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Today's Hearings</CardTitle>
              <Button variant="outline" size="sm">
                <Link to="/hearings" className="flex items-center">
                  View Schedule
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Link>
              </Button>
            </div>
            <CardDescription>
              Scheduled hearings for today
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Since we don't have hearings endpoint yet, show empty state */}
              <div className="text-center py-8 text-gray-500">
                <Calendar className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p>No hearings scheduled for today</p>
                <p className="text-sm">Check back later for updates</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      {permissions.canCreate('cases') && (
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>
              Common tasks and shortcuts
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Button variant="outline" className="h-auto p-4 flex flex-col items-center space-y-2">
                <Link to="/cases/new" className="flex flex-col items-center space-y-2">
                  <FileText className="h-8 w-8" />
                  <span>File New Case</span>
                </Link>
              </Button>
              <Button variant="outline" className="h-auto p-4 flex flex-col items-center space-y-2">
                <Link to="/hearings/schedule" className="flex flex-col items-center space-y-2">
                  <Calendar className="h-8 w-8" />
                  <span>Schedule Hearing</span>
                </Link>
              </Button>
              {permissions.canRead('reports') && (
                <Button variant="outline" className="h-auto p-4 flex flex-col items-center space-y-2">
                  <Link to="/reports" className="flex flex-col items-center space-y-2">
                    <TrendingUp className="h-8 w-8" />
                    <span>View Reports</span>
                  </Link>
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default Dashboard
