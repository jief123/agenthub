import { Link } from 'react-router-dom'
import type { ReactNode } from 'react'
import { useAuth } from '../contexts/AuthContext'

export default function Layout({ children }: { children: ReactNode }) {
  const { isAuthenticated, isAdmin, user, logout } = useAuth()

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center gap-6">
        <Link to="/" className="font-bold text-lg text-gray-900 hover:text-blue-600 transition-colors">
          AgentHub
        </Link>
        <Link to="/search" className="text-sm text-gray-600 hover:text-gray-900">Search</Link>
        {isAdmin && (
          <Link to="/admin" className="text-sm text-gray-600 hover:text-gray-900">Admin</Link>
        )}
        <div className="ml-auto flex items-center gap-4">
          {isAuthenticated ? (
            <>
              <Link to="/profile" className="text-sm text-gray-600 hover:text-gray-900">
                {user?.username}
              </Link>
              <button onClick={logout} className="text-sm text-gray-400 hover:text-gray-600">
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-sm text-gray-600 hover:text-gray-900">Login</Link>
              <Link to="/register" className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-md hover:bg-blue-700">
                Register
              </Link>
            </>
          )}
        </div>
      </nav>
      <main className="max-w-5xl mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  )
}
