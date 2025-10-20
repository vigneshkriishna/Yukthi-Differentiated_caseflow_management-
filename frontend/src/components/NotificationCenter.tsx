import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Bell, 
  X, 
  CheckCircle, 
  AlertTriangle, 
  Info, 
  Calendar,
  Gavel,
  Brain,
  Clock
} from 'lucide-react'

interface Notification {
  id: string
  type: 'success' | 'warning' | 'info' | 'schedule'
  title: string
  message: string
  timestamp: Date
  read: boolean
}

const NotificationCenter: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    // Generate sample notifications based on system activity
    const generateNotifications = () => {
      const now = new Date()
      const sampleNotifications: Notification[] = [
        {
          id: '1',
          type: 'schedule',
          title: 'Smart Scheduling Update',
          message: 'AI optimization completed. 5 new hearing slots assigned.',
          timestamp: new Date(now.getTime() - 5 * 60 * 1000), // 5 minutes ago
          read: false
        },
        {
          id: '2',
          type: 'success',
          title: 'BNS Classification Complete',
          message: 'Case FIR/2024/001/DEL classified successfully under BNS Section 103.',
          timestamp: new Date(now.getTime() - 12 * 60 * 1000), // 12 minutes ago
          read: false
        },
        {
          id: '3',
          type: 'info',
          title: 'System Health Check',
          message: 'All systems operational. Database connectivity: 100%',
          timestamp: new Date(now.getTime() - 25 * 60 * 1000), // 25 minutes ago
          read: true
        },
        {
          id: '4',
          type: 'warning',
          title: 'Pending Case Alert',
          message: 'Case SC/2024/007/BLR requires judicial review within 24 hours.',
          timestamp: new Date(now.getTime() - 1 * 60 * 60 * 1000), // 1 hour ago
          read: false
        }
      ]
      setNotifications(sampleNotifications)
    }

    generateNotifications()
    // Update notifications every 2 minutes
    const interval = setInterval(generateNotifications, 2 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  const unreadCount = notifications.filter(n => !n.read).length

  const markAsRead = (id: string) => {
    setNotifications(prev => 
      prev.map(n => n.id === id ? { ...n, read: true } : n)
    )
  }

  const markAllAsRead = () => {
    setNotifications(prev => 
      prev.map(n => ({ ...n, read: true }))
    )
  }

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />
      case 'schedule':
        return <Calendar className="h-4 w-4 text-blue-600" />
      default:
        return <Info className="h-4 w-4 text-blue-600" />
    }
  }

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'border-l-green-500 bg-green-50'
      case 'warning':
        return 'border-l-yellow-500 bg-yellow-50'
      case 'schedule':
        return 'border-l-blue-500 bg-blue-50'
      default:
        return 'border-l-gray-500 bg-gray-50'
    }
  }

  const formatTimestamp = (timestamp: Date) => {
    const now = new Date()
    const diffMs = now.getTime() - timestamp.getTime()
    const diffMinutes = Math.floor(diffMs / (1000 * 60))
    const diffHours = Math.floor(diffMinutes / 60)

    if (diffMinutes < 1) return 'Just now'
    if (diffMinutes < 60) return `${diffMinutes}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    return timestamp.toLocaleDateString()
  }

  return (
    <div className="relative">
      <Button
        variant="outline"
        size="sm"
        onClick={() => setIsOpen(!isOpen)}
        className="relative"
      >
        <Bell className="h-4 w-4" />
        {unreadCount > 0 && (
          <Badge 
            variant="destructive" 
            className="absolute -top-2 -right-2 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs"
          >
            {unreadCount}
          </Badge>
        )}
      </Button>

      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-80 z-50">
          <Card className="shadow-lg border-0 bg-white">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium">Notifications</CardTitle>
                <div className="flex items-center space-x-2">
                  {unreadCount > 0 && (
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={markAllAsRead}
                      className="text-xs"
                    >
                      Mark all read
                    </Button>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setIsOpen(false)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="p-0 max-h-96 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="p-4 text-center text-gray-500 text-sm">
                  No notifications
                </div>
              ) : (
                <div className="space-y-1">
                  {notifications.map((notification) => (
                    <div
                      key={notification.id}
                      className={`p-3 border-l-4 cursor-pointer transition-colors hover:bg-gray-50 ${
                        getNotificationColor(notification.type)
                      } ${!notification.read ? 'bg-opacity-100' : 'bg-opacity-30'}`}
                      onClick={() => markAsRead(notification.id)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-2 flex-1">
                          {getNotificationIcon(notification.type)}
                          <div className="flex-1 min-w-0">
                            <p className={`text-sm font-medium ${
                              !notification.read ? 'text-gray-900' : 'text-gray-600'
                            }`}>
                              {notification.title}
                            </p>
                            <p className="text-xs text-gray-500 mt-1">
                              {notification.message}
                            </p>
                            <p className="text-xs text-gray-400 mt-1 flex items-center">
                              <Clock className="h-3 w-3 mr-1" />
                              {formatTimestamp(notification.timestamp)}
                            </p>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation()
                            removeNotification(notification.id)
                          }}
                          className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 hover:bg-red-100"
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      </div>
                      {!notification.read && (
                        <div className="absolute left-1 top-3 w-2 h-2 bg-blue-600 rounded-full"></div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}

export default NotificationCenter