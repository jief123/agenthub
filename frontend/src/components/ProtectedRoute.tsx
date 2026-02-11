import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) return <div className="text-center py-12 text-gray-400">Loading...</div>
  if (!isAuthenticated) return <Navigate to="/login" state={{ from: location }} replace />
  return <>{children}</>
}

export function AdminRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isAdmin, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) return <div className="text-center py-12 text-gray-400">Loading...</div>
  if (!isAuthenticated) return <Navigate to="/login" state={{ from: location }} replace />
  if (!isAdmin) return <Navigate to="/" replace />
  return <>{children}</>
}
