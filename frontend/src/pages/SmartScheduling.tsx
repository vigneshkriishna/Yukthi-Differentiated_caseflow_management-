import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Calendar, 
  Clock, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle,
  Brain,
  BarChart3,
  ArrowRight,
  Zap,
  Target
} from 'lucide-react'

interface ScheduleStats {
  totalSlots: number
  availableSlots: number
  availabilityRate: number
  benchesCount: number
  workingDays: number
}

interface OptimizationSuggestion {
  type: string
  priority: string
  message: string
  action: string
  cases?: Array<{ id: number; case_number: string }>
}

interface SchedulingSuggestions {
  status: string
  optimization_suggestions: OptimizationSuggestion[]
  total_pending_cases: number
  recommended_strategy: string
}

const SmartScheduling: React.FC = () => {
  const navigate = useNavigate()
  const [scheduleStats, setScheduleStats] = useState<ScheduleStats | null>(null)
  const [suggestions, setSuggestions] = useState<SchedulingSuggestions | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchSchedulingData()
  }, [])

  const fetchSchedulingData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Mock data until backend endpoints are available
      const mockStats: ScheduleStats = {
        totalSlots: 280,
        availableSlots: 156,
        availabilityRate: 55.7,
        benchesCount: 5,
        workingDays: 7
      }
      
      const mockSuggestions: SchedulingSuggestions = {
        status: 'success',
        total_pending_cases: 42,
        recommended_strategy: 'priority_first',
        optimization_suggestions: [
          {
            type: 'urgent_cases',
            priority: 'high',
            message: 'There are 8 urgent priority cases pending. These should be scheduled within the next 3 days.',
            action: 'immediate_scheduling',
            cases: [
              { id: 1, case_number: 'CASE-2024-001' },
              { id: 2, case_number: 'CASE-2024-005' }
            ]
          },
          {
            type: 'old_cases',
            priority: 'medium',
            message: '12 cases have been pending for more than 30 days. Consider prioritizing these.',
            action: 'prioritize_old_cases',
            cases: []
          },
          {
            type: 'capacity_optimization',
            priority: 'low',
            message: 'Court utilization is at 44.3%. You have capacity for additional hearings.',
            action: 'increase_scheduling_capacity',
            cases: []
          }
        ]
      }
      
      setScheduleStats(mockStats)
      setSuggestions(mockSuggestions)
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch scheduling data')
    } finally {
      setLoading(false)
    }
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

  const getActionIcon = (action: string) => {
    switch (action.toLowerCase()) {
      case 'immediate_scheduling':
        return <Zap className="h-4 w-4" />
      case 'prioritize_old_cases':
        return <Clock className="h-4 w-4" />
      case 'increase_scheduling_capacity':
        return <TrendingUp className="h-4 w-4" />
      default:
        return <Target className="h-4 w-4" />
    }
  }

  const handleApplySuggestion = (suggestion: OptimizationSuggestion) => {
    // Navigate to Priority Scheduling page with appropriate filter
    let priorityFilter = 'all'
    
    if (suggestion.type === 'urgent_cases') {
      priorityFilter = 'urgent'
    } else if (suggestion.type === 'old_cases') {
      priorityFilter = 'all' // Could filter by date in the future
    }
    
    // Navigate to Priority Scheduling with query params
    navigate(`/priority-scheduling?priority=${priorityFilter}&action=${suggestion.action}`)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Smart Scheduling & Analytics</h1>
          <p className="text-gray-600">AI-powered scheduling optimization and court analytics</p>
        </div>
        <Button onClick={fetchSchedulingData}>
          <Brain className="h-4 w-4 mr-2" />
          Refresh Analytics
        </Button>
      </div>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2 text-red-800">
              <AlertTriangle className="h-5 w-5" />
              <span>Error: {error}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Schedule Statistics */}
      {scheduleStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Slots</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{scheduleStats.totalSlots.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                Next 7 days across {scheduleStats.benchesCount} benches
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Available Slots</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{scheduleStats.availableSlots.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                {scheduleStats.availabilityRate.toFixed(1)}% availability rate
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Working Days</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{scheduleStats.workingDays}</div>
              <p className="text-xs text-muted-foreground">
                Weekdays in analysis period
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Court Utilization</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {(100 - scheduleStats.availabilityRate).toFixed(1)}%
              </div>
              <p className="text-xs text-muted-foreground">
                Current scheduling efficiency
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* AI Optimization Suggestions */}
      {suggestions && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center space-x-2">
                  <Brain className="h-5 w-5 text-blue-600" />
                  <span>AI Optimization Suggestions</span>
                </CardTitle>
                <CardDescription>
                  Smart recommendations for efficient case scheduling
                </CardDescription>
              </div>
              <Badge variant="outline" className="bg-blue-50 text-blue-700">
                {suggestions.total_pending_cases} Pending Cases
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            {suggestions.optimization_suggestions.length > 0 ? (
              <div className="space-y-4">
                {suggestions.optimization_suggestions.map((suggestion, index) => (
                  <div key={index} className="flex items-start space-x-4 p-4 border rounded-lg bg-gradient-to-r from-blue-50 to-purple-50">
                    <div className="flex-shrink-0 mt-1">
                      <div className={`flex items-center justify-center w-8 h-8 rounded-full ${
                        suggestion.priority === 'high' ? 'bg-red-100 text-red-600' :
                        suggestion.priority === 'medium' ? 'bg-yellow-100 text-yellow-600' :
                        'bg-green-100 text-green-600'
                      }`}>
                        {getActionIcon(suggestion.action)}
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="font-medium text-sm capitalize">{suggestion.type.replace('_', ' ')}</span>
                        <Badge className={getPriorityColor(suggestion.priority)}>
                          {suggestion.priority.toUpperCase()}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-700 mb-2">{suggestion.message}</p>
                      <p className="text-xs text-gray-500">
                        Recommended Action: {suggestion.action.replace('_', ' ').toLowerCase()}
                      </p>
                      {suggestion.cases && suggestion.cases.length > 0 && (
                        <div className="mt-2">
                          <p className="text-xs text-gray-600 mb-1">Affected Cases:</p>
                          <div className="flex flex-wrap gap-1">
                            {suggestion.cases.map((case_) => (
                              <Badge key={case_.id} variant="outline" className="text-xs">
                                {case_.case_number}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => handleApplySuggestion(suggestion)}
                      className="hover:bg-blue-50 hover:border-blue-300"
                    >
                      Apply
                      <ArrowRight className="h-3 w-3 ml-1" />
                    </Button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-500" />
                <p className="font-medium">No optimization suggestions at this time</p>
                <p className="text-sm">Your scheduling appears to be running efficiently!</p>
              </div>
            )}
            
            {suggestions.recommended_strategy && (
              <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                <div className="flex items-center space-x-2 mb-2">
                  <Target className="h-4 w-4 text-blue-600" />
                  <span className="font-medium text-blue-900">Recommended Strategy</span>
                </div>
                <p className="text-sm text-blue-700 capitalize">
                  {suggestions.recommended_strategy.replace('_', ' ')} scheduling approach
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Smart Scheduling Actions</CardTitle>
          <CardDescription>
            AI-powered scheduling tools and automation
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button variant="outline" className="h-auto p-4 flex flex-col items-center space-y-2">
              <Brain className="h-8 w-8" />
              <span>Auto-Schedule Cases</span>
              <span className="text-xs text-gray-500">Let AI optimize your schedule</span>
            </Button>
            <Button variant="outline" className="h-auto p-4 flex flex-col items-center space-y-2">
              <Calendar className="h-8 w-8" />
              <span>View Schedule Matrix</span>
              <span className="text-xs text-gray-500">Comprehensive schedule view</span>
            </Button>
            <Button variant="outline" className="h-auto p-4 flex flex-col items-center space-y-2">
              <BarChart3 className="h-8 w-8" />
              <span>Analytics Dashboard</span>
              <span className="text-xs text-gray-500">Detailed scheduling metrics</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default SmartScheduling