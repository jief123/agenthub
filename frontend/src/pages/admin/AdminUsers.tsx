import { useEffect, useState } from 'react'
import { getAdminUsers } from '../../api/client'

interface User { id: number; username: string; email: string; role: string; created_at: string }

export default function AdminUsers() {
  const [users, setUsers] = useState<User[]>([])

  useEffect(() => {
    getAdminUsers().then((d) => {
      const data = d as { items: User[] }
      setUsers(data.items || [])
    }).catch(() => {})
  }, [])

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">User Management</h1>
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50">
              <th className="text-left px-4 py-2 font-medium text-gray-600">Username</th>
              <th className="text-left px-4 py-2 font-medium text-gray-600">Email</th>
              <th className="text-left px-4 py-2 font-medium text-gray-600">Role</th>
              <th className="text-left px-4 py-2 font-medium text-gray-600">Registered</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-b border-gray-100">
                <td className="px-4 py-2 font-medium text-gray-900">{u.username}</td>
                <td className="px-4 py-2 text-gray-500">{u.email}</td>
                <td className="px-4 py-2">
                  <span className={`text-xs px-2 py-0.5 rounded-full ${u.role === 'admin' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-600'}`}>
                    {u.role}
                  </span>
                </td>
                <td className="px-4 py-2 text-gray-400">{new Date(u.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {users.length === 0 && <p className="text-center text-gray-400 py-8">No users found.</p>}
      </div>
    </div>
  )
}
