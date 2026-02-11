import { useEffect, useState } from 'react'
import { getAdminAssets, deleteAdminAsset } from '../../api/client'

interface Asset { id: number; name: string; description: string; installs: number; author: { username: string } }
interface Results { skills?: { items: Asset[] }; mcps?: { items: Asset[] }; agents?: { items: Asset[] } }

const TYPES = [
  { key: '', label: 'All' },
  { key: 'skill', label: 'Skills' },
  { key: 'mcp', label: 'MCP Servers' },
  { key: 'agent', label: 'Agents' },
]

export default function AdminAssets() {
  const [type, setType] = useState('')
  const [results, setResults] = useState<Results>({})

  const load = () => { getAdminAssets(type || undefined).then((d) => setResults(d as Results)).catch(() => {}) }
  useEffect(load, [type])

  const handleDelete = async (assetType: string, id: number) => {
    if (!confirm('Delete this asset?')) return
    await deleteAdminAsset(assetType, id)
    load()
  }

  const allItems: (Asset & { _type: string })[] = [
    ...(results.skills?.items || []).map((i) => ({ ...i, _type: 'skill' })),
    ...(results.mcps?.items || []).map((i) => ({ ...i, _type: 'mcp' })),
    ...(results.agents?.items || []).map((i) => ({ ...i, _type: 'agent' })),
  ]

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Asset Management</h1>
      <div className="flex gap-2 mb-4">
        {TYPES.map((t) => (
          <button key={t.key} onClick={() => setType(t.key)}
            className={`px-3 py-1.5 text-sm rounded-full ${type === t.key ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
            {t.label}
          </button>
        ))}
      </div>
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50">
              <th className="text-left px-4 py-2 font-medium text-gray-600">Name</th>
              <th className="text-left px-4 py-2 font-medium text-gray-600">Type</th>
              <th className="text-left px-4 py-2 font-medium text-gray-600">Owner</th>
              <th className="text-left px-4 py-2 font-medium text-gray-600">Installs</th>
              <th className="text-right px-4 py-2 font-medium text-gray-600">Actions</th>
            </tr>
          </thead>
          <tbody>
            {allItems.map((item) => (
              <tr key={`${item._type}-${item.id}`} className="border-b border-gray-100">
                <td className="px-4 py-2 font-medium text-gray-900">{item.name}</td>
                <td className="px-4 py-2 text-gray-500">{item._type}</td>
                <td className="px-4 py-2 text-gray-500">{item.author?.username}</td>
                <td className="px-4 py-2 text-gray-500">{item.installs}</td>
                <td className="px-4 py-2 text-right">
                  <button onClick={() => handleDelete(item._type, item.id)}
                    className="text-red-500 hover:text-red-700">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {allItems.length === 0 && <p className="text-center text-gray-400 py-8">No assets found.</p>}
      </div>
    </div>
  )
}
