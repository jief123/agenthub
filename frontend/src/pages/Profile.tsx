import { useEffect, useState } from 'react'
import { getMyPublished, getMyInstalled, getMyStats, regenerateApiKey } from '../api/client'
import { useAuth } from '../contexts/AuthContext'

const TABS = ['Published', 'Installed', 'API Key', 'Stats'] as const
type Tab = typeof TABS[number]

interface Asset { id: number; name: string; description: string; installs: number; version?: string }
interface InstallRecord { asset_type: string; asset_id: number; agent_type: string; installed_at: string }
interface Stats { skill_count: number; mcp_count: number; agent_count: number; total_installs: number }

export default function Profile() {
  const { user } = useAuth()
  const [tab, setTab] = useState<Tab>('Published')
  const [published, setPublished] = useState<{ skills: Asset[]; mcps: Asset[]; agents: Asset[] }>({ skills: [], mcps: [], agents: [] })
  const [installed, setInstalled] = useState<InstallRecord[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [newKey, setNewKey] = useState('')

  useEffect(() => {
    if (tab === 'Published') getMyPublished().then((d) => setPublished(d as typeof published)).catch(() => {})
    if (tab === 'Installed') getMyInstalled().then((d) => setInstalled(d as InstallRecord[])).catch(() => {})
    if (tab === 'Stats') getMyStats().then((d) => setStats(d as Stats)).catch(() => {})
  }, [tab])

  const handleRegenerate = async () => {
    if (!confirm('This will invalidate your current API Key. Continue?')) return
    const res = await regenerateApiKey() as { api_key: string }
    setNewKey(res.api_key)
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-1">{user?.username}</h1>
      <p className="text-gray-400 text-sm mb-6">{user?.email}</p>

      <div className="flex gap-1 border-b border-gray-200 mb-6">
        {TABS.map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              tab === t ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}>{t}</button>
        ))}
      </div>

      {tab === 'Published' && (
        <div className="space-y-6">
          {(['skills', 'mcps', 'agents'] as const).map((type) => {
            const items = published[type]
            if (!items.length) return null
            return (
              <div key={type}>
                <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-2">
                  {type === 'skills' ? 'Skills' : type === 'mcps' ? 'MCP Servers' : 'Agents'}
                </h3>
                <div className="space-y-2">
                  {items.map((a) => (
                    <div key={a.id} className="flex items-center justify-between bg-white rounded-lg border border-gray-200 px-4 py-3">
                      <div>
                        <div className="font-medium text-gray-900">{a.name}</div>
                        <div className="text-sm text-gray-500">{a.description?.slice(0, 80)}</div>
                      </div>
                      <div className="text-sm text-gray-400">{a.installs} installs</div>
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
          {!published.skills.length && !published.mcps.length && !published.agents.length && (
            <p className="text-center text-gray-400 py-8">You haven't published any assets yet.</p>
          )}
        </div>
      )}

      {tab === 'Installed' && (
        <div className="space-y-2">
          {installed.map((r, i) => (
            <div key={i} className="flex items-center justify-between bg-white rounded-lg border border-gray-200 px-4 py-3">
              <div className="flex items-center gap-2">
                <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">{r.asset_type}</span>
                <span className="text-sm text-gray-700">Asset #{r.asset_id}</span>
              </div>
              <div className="text-xs text-gray-400">{new Date(r.installed_at).toLocaleString()}</div>
            </div>
          ))}
          {installed.length === 0 && <p className="text-center text-gray-400 py-8">No installation records.</p>}
        </div>
      )}

      {tab === 'API Key' && (
        <div className="max-w-md">
          <p className="text-sm text-gray-500 mb-4">Your API Key is used for CLI authentication and API access.</p>
          {newKey ? (
            <div className="mb-4">
              <p className="text-sm text-gray-700 mb-2">New API Key (save it now):</p>
              <div className="bg-gray-900 text-green-400 px-4 py-3 rounded-lg font-mono text-sm break-all select-all">{newKey}</div>
            </div>
          ) : (
            <p className="text-sm text-gray-400 mb-4">Your API Key is stored securely and cannot be displayed.</p>
          )}
          <button onClick={handleRegenerate}
            className="px-4 py-2 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700">
            Regenerate API Key
          </button>
        </div>
      )}

      {tab === 'Stats' && stats && (
        <div className="grid grid-cols-2 gap-4 max-w-md">
          <div className="bg-emerald-50 text-emerald-700 rounded-lg p-4">
            <div className="text-2xl font-bold">{stats.skill_count}</div>
            <div className="text-sm">Skills Published</div>
          </div>
          <div className="bg-purple-50 text-purple-700 rounded-lg p-4">
            <div className="text-2xl font-bold">{stats.mcp_count}</div>
            <div className="text-sm">MCP Servers</div>
          </div>
          <div className="bg-amber-50 text-amber-700 rounded-lg p-4">
            <div className="text-2xl font-bold">{stats.agent_count}</div>
            <div className="text-sm">Agent Configs</div>
          </div>
          <div className="bg-blue-50 text-blue-700 rounded-lg p-4">
            <div className="text-2xl font-bold">{stats.total_installs}</div>
            <div className="text-sm">Total Installs</div>
          </div>
        </div>
      )}
    </div>
  )
}
