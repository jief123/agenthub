import { useEffect, useState } from 'react'
import { getAdminAssets, getAdminUsers } from '../../api/client'

export default function AdminDashboard() {
  const [stats, setStats] = useState({ skills: 0, mcps: 0, agents: 0, users: 0 })

  useEffect(() => {
    Promise.all([getAdminAssets(), getAdminUsers()]).then(([assets, users]) => {
      const a = assets as { skills?: { total: number }; mcps?: { total: number }; agents?: { total: number } }
      const u = users as { total: number }
      setStats({
        skills: a.skills?.total || 0,
        mcps: a.mcps?.total || 0,
        agents: a.agents?.total || 0,
        users: u.total || 0,
      })
    }).catch(() => {})
  }, [])

  const cards = [
    { label: 'Skills', value: stats.skills, color: 'bg-emerald-50 text-emerald-700' },
    { label: 'MCP Servers', value: stats.mcps, color: 'bg-purple-50 text-purple-700' },
    { label: 'Agents', value: stats.agents, color: 'bg-amber-50 text-amber-700' },
    { label: 'Users', value: stats.users, color: 'bg-blue-50 text-blue-700' },
  ]

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>
      <div className="grid grid-cols-2 gap-4">
        {cards.map((c) => (
          <div key={c.label} className={`${c.color} rounded-lg p-6`}>
            <div className="text-3xl font-bold">{c.value}</div>
            <div className="text-sm mt-1">{c.label}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
