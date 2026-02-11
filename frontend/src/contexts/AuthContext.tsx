import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { getCurrentUser, loginUser, registerUser } from '../api/client'

interface User {
  id: number
  username: string
  display_name: string | null
  email: string
  role: string
}

interface AuthContextType {
  user: User | null
  apiKey: string | null
  isLoading: boolean
  isAuthenticated: boolean
  isAdmin: boolean
  login: (email: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<string>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [apiKey, setApiKey] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      getCurrentUser()
        .then((u) => setUser(u as User))
        .catch(() => { localStorage.removeItem('token') })
        .finally(() => setIsLoading(false))
    } else {
      setIsLoading(false)
    }
  }, [])

  const login = async (email: string, password: string) => {
    const res = await loginUser(email, password) as { user: User; token: string }
    localStorage.setItem('token', res.token)
    setUser(res.user)
  }

  const register = async (username: string, email: string, password: string) => {
    const res = await registerUser(username, email, password) as { user: User; api_key: string; token: string }
    localStorage.setItem('token', res.token)
    setApiKey(res.api_key)
    setUser(res.user)
    return res.api_key
  }

  const logout = () => {
    localStorage.removeItem('token')
    setApiKey(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{
      user, apiKey, isLoading,
      isAuthenticated: !!user,
      isAdmin: user?.role === 'admin',
      login, register, logout,
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
