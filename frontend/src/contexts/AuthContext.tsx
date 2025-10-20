import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { User, UserRole } from '../types'
import { authAPI } from '../services/api'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
}

interface AuthContextType extends AuthState {
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  demoLogin: (role?: UserRole) => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [state, setState] = useState<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: true,
  })

  // Check for existing token on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    const userStr = localStorage.getItem('user')
    
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr)
        setState({
          user,
          token,
          isAuthenticated: true,
          isLoading: false,
        })
      } catch (error) {
        console.error('Error parsing stored user data:', error)
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
        setState(prev => ({ ...prev, isLoading: false }))
      }
    } else {
      setState(prev => ({ ...prev, isLoading: false }))
    }
  }, [])

  const login = async (username: string, password: string) => {
    try {
      setState(prev => ({ ...prev, isLoading: true }))
      
      const response = await authAPI.login({ username, password })
      
      if (response.data) {
        const { access_token: token, user } = response.data
        
        localStorage.setItem('access_token', token)
        localStorage.setItem('user', JSON.stringify(user))
        
        setState({
          user,
          token,
          isAuthenticated: true,
          isLoading: false,
        })
      } else {
        throw new Error('Login failed')
      }
    } catch (error) {
      setState(prev => ({ ...prev, isLoading: false }))
      throw error
    }
  }

  const demoLogin = async (role: UserRole = UserRole.PUBLIC) => {
    try {
      setState(prev => ({ ...prev, isLoading: true }))
      
      // Map roles to real backend usernames  
      const demoCredentials: Record<UserRole, { username: string; password: string }> = {
        [UserRole.ADMIN]: { username: 'admin', password: 'admin123' },
        [UserRole.JUDGE]: { username: 'judge1', password: 'demo123' },
        [UserRole.CLERK]: { username: 'clerk1', password: 'demo123' },
        [UserRole.LAWYER]: { username: 'lawyer1', password: 'demo123' },
        [UserRole.PUBLIC]: { username: 'lawyer1', password: 'demo123' }, // Using lawyer1 as fallback
      }

      const credentials = demoCredentials[role]
      const response = await authAPI.login(credentials)
      
      if (response.data) {
        const { access_token: token, user } = response.data
        
        localStorage.setItem('access_token', token)
        localStorage.setItem('user', JSON.stringify(user))
        
        setState({
          user,
          token,
          isAuthenticated: true,
          isLoading: false,
        })
      } else {
        throw new Error('Demo login failed')
      }
    } catch (error) {
      setState(prev => ({ ...prev, isLoading: false }))
      throw error
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    
    setState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    })
  }

  const value: AuthContextType = {
    ...state,
    login,
    logout,
    demoLogin,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// Permission management hook
export function usePermissions() {
  const { user } = useAuth()
  
  const hasPermission = (permission: string): boolean => {
    if (!user) return false
    
    // Admin has all permissions
    if (user.role === UserRole.ADMIN) return true
    
    // Define role-based permissions
    const rolePermissions: Record<UserRole, string[]> = {
      [UserRole.ADMIN]: ['*'], // All permissions
      [UserRole.JUDGE]: [
        'cases.read',
        'cases.update',
        'hearings.read', 
        'hearings.create',
        'hearings.update',
        'schedule.read',
        'reports.read'
      ],
      [UserRole.CLERK]: [
        'cases.read',
        'cases.create',
        'cases.update',
        'hearings.read',
        'hearings.create',
        'schedule.read',
        'documents.read',
        'documents.create',
        'documents.delete'
      ],
      [UserRole.LAWYER]: [
        'cases.read',
        'hearings.read',
        'documents.read',
        'documents.create',
        'schedule.read'
      ],
      [UserRole.PUBLIC]: [
        'cases.read',
        'hearings.read',
        'schedule.read'
      ]
    }
    
    const userPermissions = rolePermissions[user.role] || []
    return userPermissions.includes('*') || userPermissions.includes(permission)
  }
  
  const canRead = (resource: string) => hasPermission(`${resource}.read`)
  const canCreate = (resource: string) => hasPermission(`${resource}.create`)
  const canUpdate = (resource: string) => hasPermission(`${resource}.update`)
  const canDelete = (resource: string) => hasPermission(`${resource}.delete`)
  
  return {
    hasPermission,
    canRead,
    canCreate,
    canUpdate,
    canDelete,
    isAdmin: user?.role === UserRole.ADMIN,
    isJudge: user?.role === UserRole.JUDGE,
    isClerk: user?.role === UserRole.CLERK,
    isLawyer: user?.role === UserRole.LAWYER,
    isPublic: user?.role === UserRole.PUBLIC
  }
}
