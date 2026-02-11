import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function Register() {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (password !== confirm) { setError('Passwords do not match'); return }
    if (password.length < 8) { setError('Password must be at least 8 characters'); return }
    setLoading(true)
    try {
      const key = await register(username, email, password)
      setApiKey(key)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  if (apiKey) {
    return (
      <div className="max-w-sm mx-auto mt-16 text-center">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Registration Successful</h1>
        <p className="text-sm text-gray-500 mb-4">Save your API Key — it won't be shown again:</p>
        <div className="bg-gray-900 text-green-400 px-4 py-3 rounded-lg font-mono text-sm mb-6 break-all select-all">
          {apiKey}
        </div>
        <button onClick={() => navigate('/')} className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">
          Go to Home
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-sm mx-auto mt-16">
      <h1 className="text-2xl font-bold text-gray-900 mb-6 text-center">Register</h1>
      {error && <div className="bg-red-50 text-red-600 text-sm px-4 py-2 rounded-lg mb-4">{error}</div>}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">Username</label>
          <input id="username" type="text" required minLength={3} maxLength={64} value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
        </div>
        <div>
          <label htmlFor="reg-email" className="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input id="reg-email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
        </div>
        <div>
          <label htmlFor="reg-password" className="block text-sm font-medium text-gray-700 mb-1">Password</label>
          <input id="reg-password" type="password" required minLength={8} value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
        </div>
        <div>
          <label htmlFor="reg-confirm" className="block text-sm font-medium text-gray-700 mb-1">Confirm Password</label>
          <input id="reg-confirm" type="password" required value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
        </div>
        <button type="submit" disabled={loading}
          className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50">
          {loading ? 'Registering...' : 'Register'}
        </button>
      </form>
      <p className="text-center text-sm text-gray-500 mt-4">
        Already have an account? <Link to="/login" className="text-blue-600 hover:underline">Login</Link>
      </p>
    </div>
  )
}
