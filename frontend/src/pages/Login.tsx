import React, { useState } from 'react'
import { Navigate, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Scale, Eye, EyeOff, Loader2 } from 'lucide-react'
import { UserRole } from '../types'
import toast from 'react-hot-toast'

const Login: React.FC = () => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const { login, demoLogin, isAuthenticated } = useAuth()

  // Redirect if already authenticated
  if (isAuthenticated) {
    return <Navigate to="/" replace />
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!username.trim() || !password.trim()) return

    setIsLoading(true)

    try {
      await login(username.trim(), password)
      toast.success('Login successful!')
    } catch (err: any) {
      toast.error(err.message || 'Login failed')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDemoLogin = async (role: UserRole) => {
    setIsLoading(true)
    try {
      await demoLogin(role)
      toast.success(`Demo login as ${role} successful!`)
    } catch (err: any) {
      toast.error(err.message || 'Demo login failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="flex justify-center">
            <div className="flex items-center space-x-2">
              <Scale className="h-12 w-12 text-primary" />
            </div>
          </div>
          <h2 className="mt-6 text-3xl font-bold text-gray-900">
            DCM System
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Smart Differentiated Case Flow Management
          </p>
          <p className="text-sm text-gray-600">
            Sign in to your account
          </p>
        </div>

        {/* Login Form */}
        <Card>
          <CardHeader>
            <CardTitle>Welcome Back</CardTitle>
            <CardDescription>
              Enter your credentials to access the system
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form className="space-y-6" onSubmit={handleSubmit}>

              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                  Username
                </label>
                <div className="mt-1">
                  <Input
                    id="username"
                    name="username"
                    type="text"
                    autoComplete="username"
                    required
                    placeholder="Enter your username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    disabled={isLoading}
                  />
                </div>
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                  Password
                </label>
                <div className="mt-1 relative">
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    required
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    disabled={isLoading}
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4 text-gray-400" />
                    ) : (
                      <Eye className="h-4 w-4 text-gray-400" />
                    )}
                  </button>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <input
                    id="remember-me"
                    name="remember-me"
                    type="checkbox"
                    className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                  />
                  <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-900">
                    Remember me
                  </label>
                </div>

                <div className="text-sm">
                  <Link
                    to="/forgot-password"
                    className="font-medium text-primary hover:text-primary/80"
                  >
                    Forgot your password?
                  </Link>
                </div>
              </div>

              <div>
                <Button
                  type="submit"
                  className="w-full"
                  disabled={isLoading || !username.trim() || !password.trim()}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Signing in...
                    </>
                  ) : (
                    'Sign in'
                  )}
                </Button>
              </div>

              <div className="text-center">
                <p className="text-sm text-gray-600">
                  Don't have an account?{' '}
                  <Link
                    to="/register"
                    className="font-medium text-primary hover:text-primary/80"
                  >
                    Contact your administrator
                  </Link>
                </p>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Demo Credentials */}
        <Card className="bg-blue-50 border-blue-200">
          <CardHeader>
            <CardTitle className="text-sm text-blue-800">Test Credentials</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-blue-700">
            <div className="space-y-2">
              <div>
                <strong>Admin:</strong> admin / admin123
              </div>
              <div>
                <strong>Judge:</strong> judge1 / demo123
              </div>
              <div>
                <strong>Clerk:</strong> clerk1 / demo123
              </div>
              <div>
                <strong>Lawyer:</strong> lawyer1 / demo123
              </div>
              <div>
                <em>Note: Use the exact credentials shown above</em>
              </div>
            </div>
            
            <div className="mt-4 space-y-2">
              <p className="text-xs text-blue-600 mb-2">Quick Demo Login:</p>
              <div className="grid grid-cols-2 gap-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => handleDemoLogin(UserRole.ADMIN)}
                  disabled={isLoading}
                  className="text-xs"
                >
                  Admin Demo
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => handleDemoLogin(UserRole.JUDGE)}
                  disabled={isLoading}
                  className="text-xs"
                >
                  Judge Demo
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => handleDemoLogin(UserRole.CLERK)}
                  disabled={isLoading}
                  className="text-xs"
                >
                  Clerk Demo
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => handleDemoLogin(UserRole.PUBLIC)}
                  disabled={isLoading}
                  className="text-xs"
                >
                  Public Demo
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center text-xs text-gray-500">
          <p>
            &copy; 2024 Smart Differentiated Case Flow Management System.
          </p>
          <p>
            Built with BNS Assist - Powered by AI for Legal Excellence.
          </p>
        </div>
      </div>
    </div>
  )
}

export default Login
