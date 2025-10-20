import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  Activity, 
  Database, 
  Server, 
  Brain, 
  Calendar,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Zap,
  TrendingUp,
  Clock
} from 'lucide-react'

interface SystemHealth {
  service: string
  status: 'healthy' | 'warning' | 'down'
  latency?: number
  uptime?: string
  details?: string
  icon: React.ComponentType<any>
}

const SystemHealthWidget: React.FC = () => {
  const [healthData, setHealthData] = useState<SystemHealth[]>([])
  const [lastChecked, setLastChecked] = useState<Date>(new Date())

  useEffect(() => {
    checkSystemHealth()
    const interval = setInterval(checkSystemHealth, 10000) // Check every 10 seconds
    return () => clearInterval(interval)
  }, [])

  const checkSystemHealth = async () => {
    try {
      // Simulate real health checks
      const mockHealthData: SystemHealth[] = [
        {
          service: 'Backend API',
          status: 'healthy',
          latency: Math.floor(Math.random() * 50) + 20, // 20-70ms
          uptime: '99.9%',
          details: 'All endpoints responding',
          icon: Server
        },
        {
          service: 'Database',
          status: 'healthy',
          latency: Math.floor(Math.random() * 30) + 10, // 10-40ms
          uptime: '100%',
          details: 'Connection pool healthy',
          icon: Database
        },
        {
          service: 'AI Classification',
          status: Math.random() > 0.9 ? 'warning' : 'healthy',
          latency: Math.floor(Math.random() * 200) + 100, // 100-300ms
          uptime: '98.7%',
          details: 'Model inference active',
          icon: Brain
        },
        {
          service: 'Smart Scheduling',
          status: 'healthy',
          latency: Math.floor(Math.random() * 80) + 50, // 50-130ms
          uptime: '99.5%',
          details: 'Optimization engine running',
          icon: Calendar
        },
        {
          service: 'Real-time Analytics',
          status: Math.random() > 0.95 ? 'warning' : 'healthy',
          latency: Math.floor(Math.random() * 40) + 15, // 15-55ms
          uptime: '99.8%',
          details: 'Dashboard updates active',
          icon: TrendingUp
        }
      ]

      setHealthData(mockHealthData)
      setLastChecked(new Date())
    } catch (error) {
      console.error('Health check failed:', error)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />
      case 'down':
        return <XCircle className="h-4 w-4 text-red-600" />
      default:
        return <CheckCircle className="h-4 w-4 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-700 bg-green-50 border-green-200'
      case 'warning':
        return 'text-yellow-700 bg-yellow-50 border-yellow-200'
      case 'down':
        return 'text-red-700 bg-red-50 border-red-200'
      default:
        return 'text-gray-700 bg-gray-50 border-gray-200'
    }
  }

  const getLatencyColor = (latency: number) => {
    if (latency < 50) return 'text-green-600'
    if (latency < 100) return 'text-yellow-600'
    return 'text-red-600'
  }

  const overallStatus = healthData.every(service => service.status === 'healthy') 
    ? 'healthy' 
    : healthData.some(service => service.status === 'down') 
    ? 'down' 
    : 'warning'

  return (
    <Card className="h-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center space-x-2 text-lg">
            <Activity className="h-5 w-5 text-blue-600" />
            <span>System Health</span>
          </CardTitle>
          <div className="flex items-center space-x-2">
            <Badge 
              variant="outline" 
              className={`${getStatusColor(overallStatus)} font-medium`}
            >
              {getStatusIcon(overallStatus)}
              <span className="ml-1 capitalize">{overallStatus}</span>
            </Badge>
          </div>
        </div>
        <p className="text-sm text-gray-500 flex items-center">
          <Clock className="h-3 w-3 mr-1" />
          Last checked: {lastChecked.toLocaleTimeString()}
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        {healthData.map((service, index) => {
          const IconComponent = service.icon
          return (
            <div 
              key={index}
              className="flex items-center justify-between p-3 border rounded-lg bg-white hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center space-x-3 flex-1">
                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-gray-100">
                  <IconComponent className="h-4 w-4 text-gray-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-gray-900">{service.service}</p>
                    <div className="flex items-center space-x-2">
                      {service.latency && (
                        <span className={`text-xs ${getLatencyColor(service.latency)}`}>
                          {service.latency}ms
                        </span>
                      )}
                      {getStatusIcon(service.status)}
                    </div>
                  </div>
                  <div className="flex items-center justify-between mt-1">
                    <p className="text-xs text-gray-500">{service.details}</p>
                    {service.uptime && (
                      <span className="text-xs text-gray-400">
                        {service.uptime} uptime
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )
        })}

        {/* Quick Actions */}
        <div className="pt-4 border-t">
          <div className="grid grid-cols-2 gap-2">
            <button className="flex items-center justify-center p-2 text-xs font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
              <Zap className="h-3 w-3 mr-1" />
              Run Diagnostics
            </button>
            <button className="flex items-center justify-center p-2 text-xs font-medium text-gray-600 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
              <Activity className="h-3 w-3 mr-1" />
              View Logs
            </button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default SystemHealthWidget