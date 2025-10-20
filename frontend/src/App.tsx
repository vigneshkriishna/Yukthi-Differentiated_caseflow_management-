import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'
import EnhancedDashboard from './pages/EnhancedDashboard'
import AIDashboard from './pages/AIDashboard'
import Login from './pages/Login'
import Cases from './pages/Cases'
import NewCase from './pages/NewCase'
import Documents from './pages/Documents'
import Hearings from './pages/Hearings'
import SmartScheduling from './pages/SmartScheduling'
import PriorityScheduling from './pages/PriorityScheduling'
import Reports from './pages/Reports'
import Settings from './pages/Settings'
import Users from './pages/Users'
import './index.css'

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          
          {/* Protected routes */}
          <Route path="/" element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }>
            <Route index element={<EnhancedDashboard />} />
            <Route path="ai-dashboard" element={<AIDashboard />} />
            <Route path="cases" element={<Cases />} />
            <Route path="cases/new" element={<NewCase />} />
            <Route path="cases/:id" element={<div className="p-8 text-center text-gray-600">Case Details (Coming Soon)</div>} />
            <Route path="documents" element={<Documents />} />
            <Route path="hearings" element={<Hearings />} />
            <Route path="scheduling" element={<SmartScheduling />} />
            <Route path="priority-scheduling" element={
              <ProtectedRoute requiredRoles={['ADMIN', 'CLERK']}>
                <PriorityScheduling />
              </ProtectedRoute>
            } />
            <Route path="reports" element={
              <ProtectedRoute requiredRoles={['ADMIN', 'JUDGE', 'CLERK']}>
                <Reports />
              </ProtectedRoute>
            } />
            <Route path="users" element={
              <ProtectedRoute requiredRoles={['ADMIN']}>
                <Users />
              </ProtectedRoute>
            } />
            <Route path="settings" element={<Settings />} />
          </Route>

          {/* Catch all route */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </AuthProvider>
  )
}

export default App
